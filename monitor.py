#!/usr/bin/python

import subprocess
import sys
import re

conf_update_time = 300
conf_rrd_file = "/opt/etc/monitor.rrd"
conf_dest_dir = "/volume1/web/stats"
conf_filename = "index.html"

volumes = [ 1, 2, 3, 4, 5 ]
hds     = [ "/dev/sda", "/dev/sdb" ]

#
#
#

def run_command(cmd):
    try:
        return subprocess.check_output(cmd.split())
    except:
        return None

def search(pattern, string):
    return re.search(pattern, string, re.MULTILINE)

def int_array(array):
    return [ int(i) for i in array ]

#
#
#

class Volume:
    def __init__(self):
        self._cmd = run_command("df -m")
	self._data = { }

    def store(self, dev):
        m = search("^" + dev + "\s+(\d+)\s+(\d+)", self._cmd)
        [ total, used ] = int_array(m.group(1, 2))
        self._data[dev] = [ total, used, 100.0 * used / total ]

    def show(self):
	print self._data

class SmartData:
    def __init__(self, hdlist):
	self._cmd = { }
	self._data = { }

	for i in hdlist:
            self._cmd[i] = run_command("smartctl -d ata -A " + i)
	    self._data[i] = { }

    def store(self, hd, parm):
	if self._cmd[hd] == None:
            self._data[hd][parm] = 0
        else:
            m = search(parm + " .* (\d+)$", self._cmd[hd])
            self._data[hd][parm] = m.group(1)

    def show(self):
	print self._data

#
#
#

def store(hd, vol):
    vol.store("/dev/md0")
    
    for i in volumes:
        vol.store("/dev/vg1/volume_%d" % (i))
    
    for i in hds:
        hd.store(i, "Temperature_Celsius")
        hd.store(i, "Power_On_Hours")
        hd.store(i, "Start_Stop_Count")
    

def show(hd, vol):
    hd.show()
    vol.show()


if __name__ == "__main__":

    if len(sys.argv) < 2:
	print "Usage: %s [ show | update | report ]" % (sys.argv[0])
	sys.exit(0)

    if sys.argv[1] == "show":
        vol = Volume()
        hd = SmartData(hds)
	store(hd, vol)
        show(hd, vol)

