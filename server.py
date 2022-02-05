import time
from flask import Flask, json, request
from dronekit import connect, VehicleMode
from pymavlink import mavutil
from apscheduler.schedulers.background import BackgroundScheduler
import argparse
import requests
import os

sitl = False

api = Flask(__name__)
scheduler = BackgroundScheduler()
heartbeatScheduler = BackgroundScheduler()
token = ""


def maintain_throttle():
    #For SITL
    vehicle.channels.overrides['3'] = 1500


@api.route('/take-off', methods=['POST'])
def take_off():
    if('altitude' in request.data):
        altitude = request.json["altitude"]
    else:
        altitude = 10
    if('username' in request.data):
        username = request.json["username"]
    else:
        return json.dumps({"success": False, "message": "username required"}), 401
    if('password' in request.data):
        password = request.json["password"]
    else:
        return json.dumps({"success": False, "message": "password required"}), 401

    authenticated = checkAuth(username, password)
    if(authenticated):
        print "Basic pre-arm checks"

        print "Arming motors"
        vehicle.mode = VehicleMode("GUIDED")
        vehicle.armed = True

        while not vehicle.armed:
            print " Waiting for arming..."
            time.sleep(1)

        print "Taking off!"
        vehicle.simple_takeoff(altitude)
        while True:
            print " Altitude: ", vehicle.location.global_relative_frame.alt
            # Break and return from function just below target altitude.
            if vehicle.location.global_relative_frame.alt >= altitude * 0.95:
                print "Reached target altitude"
                vehicle.mode = VehicleMode("LOITER")
                if sitl:
                    scheduler.resume()
                # print " Ch3: %s" % vehicle.channels['3']
                # land()
                break
            time.sleep(1)
        return json.dumps({"success": True}), 201
    else:
        return json.dumps({"success": False, "message": "invalid username/password"}), 401


@api.route('/land', methods=['POST'])
def land():
    if ('username' in request.data):
        username = request.json["username"]
    else:
        return json.dumps({"success": False, "message": "username required"}), 401
    if ('password' in request.data):
        password = request.json["password"]
    else:
        return json.dumps({"success": False, "message": "password required"}), 401

    authenticated = checkAuth(username, password)
    if (authenticated):
        print "Vehicle in LAND mode"
        if sitl:
            scheduler.pause()
        vehicle.mode = VehicleMode("LAND")
        # while not vehicle.location.global_relative_frame.alt == 0:
        #     if vehicle.location.global_relative_frame.alt < 2:
        #         set_velocity_body(vehicle, 0, 0, 0.1)
        vehicle.armed = False
        return json.dumps({"success": True}), 201
    else:
        return json.dumps({"success": False, "message": "invalid username/password"}), 401

def set_velocity_body(vehicle, vx, vy, vz):
    """ Remember: vz is positive downward!!!
    http://ardupilot.org/dev/docs/copter-commands-in-guided-mode.html

    Bitmask to indicate which dimensions should be ignored by the vehicle
    (a value of 0b0000000000000000 or 0b0000001000000000 indicates that
    none of the setpoint dimensions should be ignored). Mapping:
    bit 1: x,  bit 2: y,  bit 3: z,
    bit 4: vx, bit 5: vy, bit 6: vz,
    bit 7: ax, bit 8: ay, bit 9:
    """
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
    0,
    0, 0,
    mavutil.mavlink.MAV_FRAME_BODY_NED,
    0b0000111111000111,  # -- BITMASK -> Consider only the velocities
    0, 0, 0,  # -- POSITION
    vx, vy, vz,  # -- VELOCITY
    0, 0, 0,  # -- ACCELERATIONS
    0, 0)
    vehicle.send_mavlink(msg)
    vehicle.flush()

def heartbeatRequest(remoteUrl='http://localhost:8080/'):
    global vehicle
    global token
    token = login()
    query={
        "globalLat": vehicle.location.global_frame.lat,
        "globalLon": vehicle.location.global_frame.lon,
        "globalAlt": vehicle.location.global_frame.alt,
        "relativeLat": vehicle.location.global_relative_frame.lat,
        "relativeLon": vehicle.location.global_relative_frame.lon,
        "relativeAlt": vehicle.location.global_relative_frame.alt,
        "yaw": vehicle.attitude.yaw,
        "pitch": vehicle.attitude.pitch,
        "roll": vehicle.attitude.roll,
        "velocityX": vehicle.velocity[0],
        "velocityY": vehicle.velocity[1],
        "velocityZ": vehicle.velocity[2],
        "groundSpeed": vehicle.groundspeed,
        "isArmable": vehicle.is_armable,
        "armed": vehicle.armed,
        "batVoltage": vehicle.battery.voltage,
        "batLevel": vehicle.battery.level,
        "batCurrent": vehicle.battery.current,
        "gpsFix": vehicle.gps_0.fix_type,
        "gpsNumSat": vehicle.gps_0.satellites_visible,
        "mode": vehicle.mode.name,
        "systemStatus": vehicle.system_status.state
    }
    headers = {
        "Authorization": "Bearer " + token
    }
    return requests.post(remoteUrl + "droneApi/heartbeat", json=query, headers=headers)

def login():
    global token
    query={
        "password": os.getenv('DRONE_PASSWORD'),
        "rememberMe": False,
        "username": os.getenv('DRONE_USERNAME'),
    }
    response = requests.post("http://localhost:8080/droneApi/authenticate", json=query)
    token = response.json()["id_token"]
    return token


def checkAuth(username, password):
    correctUsername = os.getenv('DRONE_USERNAME')
    correctPassword = os.getenv('DRONE_PASSWORD')
    if(username == correctUsername and password == correctPassword):
        return True


if __name__ == "__main__":
    # Initialize parser
    connection_string = '/dev/ttyAMA0'
    baud = 921600
    host = "localhost"

    parser = argparse.ArgumentParser()

    # Adding optional argument
    parser.add_argument("-c", "--connection", help="Connection String (eg: /dev/ttyAMA0)")
    parser.add_argument("-b", "--baud", help="Set baud rate")
    parser.add_argument("-H", "--host", required=True, help="Set host ip address")
    parser.add_argument("-m", "--mode", help="Set mode (real/sitl)")

    # Read arguments from command line
    args = parser.parse_args()

    if(args.connection):
        connection_string = args.connection
    if args.baud:
        baud = args.baud
    if args.host:
        host = args.host
    if args.mode:
        if args.mode == "sitl":
            sitl = True

    print "Connecting to Vehicle"

    print("Connecting to vehicle on: %s" % (connection_string,))
    vehicle = connect(connection_string, wait_ready=True, baud=baud)
    # vehicle = connect('tcp:127.0.0.1:5763', wait_ready=True)
    heartbeatScheduler.add_job(func=heartbeatRequest, trigger="interval", seconds=5)
    heartbeatScheduler.start()
    if sitl:
        scheduler.add_job(func=maintain_throttle, trigger="interval", seconds=1)
        scheduler.start()
        scheduler.pause()

    api.run(host=host, port=5000)
