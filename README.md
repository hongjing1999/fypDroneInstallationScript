This project is for Final Year Project Purpose only

**Configure wwan0 interface**

1\. Create new file with wwan0 as filename in /etc/network/interfaces.d/

Sample configuration for wwan0:

                            `auto wwan0
                                iface wwan0 inet manual
                                    pre-up uhubctl -a off -l 1-1 -p 2
                                    pre-up /bin/sleep 1
                                    pre-up uhubctl -a on -l 1-1 -p 2
                                    pre-up /bin/sleep 30
                                    pre-up ifconfig wwan0 down
                                    pre-up for _ in $(seq 1 10); do /usr/bin/test -c /dev/cdc-wdm0 && break; /bin/sleep 1; done
                                    pre-up for _ in $(seq 1 10); do /usr/bin/qmicli -d /dev/cdc-wdm0 --nas-get-signal-strength && break; /bin/sleep 1; done
                                    pre-up /usr/local/bin/qmi-network-raw /dev/cdc-wdm0 start
                                    pre-up udhcpc -i wwan0
                                    post-down /usr/local/bin/qmi-network-raw /dev/cdc-wdm0 stop` 
                          

  

**Setting up VPN**

1\. Download VPN configuration file

![](../../assets/image/downloadConfigButton.png)

2\. Install Wireguard in companion computer using this command

                            `sudo apt install wireguard` 
                          

3\. Copy the configuration file to /etc/wireguard/wg0.conf in companion computer

To start the VPN, run

                            `wg-quick up wg0` 
                          

  

**Declaring environment variable**

1\. Set HOST to VPN ip address from the VPN configuration file

![](../../assets/image/vpnconfiguration.png)

2\. Set DRONE\_USERNAME to the username of drone when registering the drone

3\. Set DRONE\_PASSWORD to the password of drone when registering the drone

                            `export HOST=ip_address
                                export DRONE_USERNAME=username
                                export DRONE_PASSWORD=password` 
                          

4\. To export the environment variable during every startup, write the command in /etc/rc.local

![](../../assets/image/rclocal.png)  

**Installing scripts**

1\. Download Installation script

![](../../assets/image/downloadScriptButton.png)

2\. Copy it to the companion computer and extract it using the command:

                            `tar -xvf install.tar.xz` 
                          

3\. Change directory into the extracted directory

                            `cd install` 
                          

4\. Run the installation script

                            `sudo sh install.sh` 
                          

  

**Modifying serial interface of flight controller**

The default serial interface used is /dev/ttyAMA0. If you want to change it add -c option in /bin/fyp\_drone/server.sh

                              `python /bin/fyp_drone/server.py -H $HOST -c /dev/ttyUSB0` 
                          

  

**Disabling video streaming**

Comment out the line

                              `sh /bin/fyp_drone/start_camera.sh &` 
                          

in /bin/fyp\_drone/start\_drone.sh
