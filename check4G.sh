#!/bin/sh

while :
do
    echo "Signal Strength"
    INFO=$(/usr/bin/qmicli -d /dev/cdc-wdm0 --nas-get-signal-info)
    if [ ! -z "$INFO" ]
    then
        CONNECTION_TYPE="${INFO#*info}"
        CONNECTION_TYPE="${CONNECTION_TYPE%%:*}"
        echo $CONNECTION_TYPE
        
        #No LTE try to connect to 4G
        if [ $CONNECTION_TYPE = WCDMA ]
        then
            ifdown wwan0 
            ifup wwan0
            systemctl stop wg-quick@wg0
            sleep 2
            systemctl start wg-quick@wg0
            sleep 4
            continue
        fi

        #connected to 4G check signal strength
        TMP="${INFO#*RSSI: }"
        TMP="${TMP%%dBm*}"
        STRENGTH=$(echo $TMP | grep -Eo '[+-]?[0-9]+([.][0-9]+)?')
        echo $STRENGTH
        if [ $STRENGTH -ge -30 ]
        then SIGNAL_QUALITY="Amazing"
        elif [ $STRENGTH -ge -67 ]
        then SIGNAL_QUALITY="Very Good"
        elif [ $STRENGTH -ge -70 ]
        then SIGNAL_QUALITY="Okay"
        elif [ $STRENGTH -ge -90 ]
        then SIGNAL_QUALITY="Not Good"
        else SIGNAL_QUALITY="Unusable"
        fi
        echo $SIGNAL_QUALITY
        ip4=$(/sbin/ip -o -4 addr list wwan0 | awk '{print $4}' | cut -d/ -f1)
        #Empty Ip Address
        if [ -z "$ip4" ]
        then 
            ifdown wwan0
            ifup wwan0
            systemctl stop wg-quick@wg0
            sleep 2
            systemctl start wg-quick@wg0
        else 
            echo $ip4 | grep 169.254. &&  VALID_IP=false || VALID_IP=true
            #Ip address is invalid
            if [ "$VALID_IP" = false ]
            then
                ifdown wwan0 
                ifup wwan0
                systemctl stop wg-quick@wg0
                sleep 2
                systemctl start wg-quick@wg0
            fi
        fi
    fi
    sleep 2
done
