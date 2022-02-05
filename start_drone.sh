#!/bin/bash

sh /bin/fyp_drone/check4G.sh &
sh /bin/fyp_drone/start_camera.sh &
sh /bin/fyp_drone/server.sh &
