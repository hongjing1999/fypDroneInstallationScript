#!/bin/bash

. /bin/fyp_drone/venv/bin/activate
python /bin/fyp_drone/server.py -H $HOST

exit 0