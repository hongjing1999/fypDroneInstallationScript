#!/usr/bin/env python
import os

contain =False
with open('/etc/rc.local') as fin:
    with open('/etc/rc.local.TMP', 'w') as fout:
        for line in fin:
            if 'sh /bin/fyp_drone/start_drone.sh' in line:
                contain = True
            if 'exit 0' in line and contain == False:
                fout.write('sh /bin/fyp_drone/start_drone.sh\n')
            fout.write(line)

# save original version (just in case)
os.rename('/etc/rc.local', '/etc/rc.local.jic')

os.rename('/etc/rc.local.TMP', '/etc/rc.local')
