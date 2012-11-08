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
ifaces	= [ "eth0" ]

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

    def parse(self, dev):
        m = search("^" + dev + "\s+(\d+)\s+(\d+)", self._cmd)
        [ total, used ] = int_array(m.group(1, 2))
        self._data[dev] = [ total, used, 100.0 * used / total ]

    def show(self):
	print "Volume data:"
	for i in sorted(self._data.keys()):
            print "    %s:" % (i)
            print "        Total size : %d" % (self._data[i][0])
            print "        Used size  : %d" % (self._data[i][1])
            print "        Percent    : %4.1f%%" % (self._data[i][2])
            print

class SmartData:
    def __init__(self, hdlist):
	self._cmd = { }
	self._data = { }

	for i in hdlist:
            self._cmd[i] = run_command("smartctl -d ata -A " + i)
	    self._data[i] = { }

    def parse(self, hd, parm):
	if self._cmd[hd] == None:
            self._data[hd][parm] = 0
        else:
            m = search(parm + " .* (\d+)$", self._cmd[hd])
            self._data[hd][parm] = int(m.group(1))

    def show(self):
        print "Hard disk data:"
	for i in sorted(self._data.keys()):
            print "    %s:" % (i)
	    for j in self._data[i].keys():
                print "        %-20.20s: %d" % (j, self._data[i][j])
            print

class Interface:
    def __init__(self, iflist):
        self._cmd = { }
        self._data = { }

        for i in iflist:
            self._cmd[i] = run_command("ifconfig " + i)

    def parse(self, iface):
        m = search("RX bytes:(\d+) .*TX bytes:(\d+)", self._cmd[iface])
        self._data[iface] = int_array(m.group(1, 2))

    def show(self):
        print "Network interface data:"
	for i in sorted(self._data.keys()):
            print "    %s:" % (i)
            print "        Rx bytes : %d" % (self._data[i][0])
            print "        Tx bytes : %d" % (self._data[i][1])
            print
#
#
#

def parse(hd, vol, iface):
    vol.parse("/dev/md0")
    
    for i in volumes:
        vol.parse("/dev/vg1/volume_%d" % (i))
    
    for i in hds:
        hd.parse(i, "Temperature_Celsius")
        hd.parse(i, "Power_On_Hours")
        hd.parse(i, "Start_Stop_Count")
    
    for i in ifaces:
        iface.parse(i)

def show(hd, vol, iface):
    hd.show()
    vol.show()
    iface.show()


if __name__ == "__main__":

    if len(sys.argv) < 2:
	print "Usage: %s [ show | update | report ]" % (sys.argv[0])
	sys.exit(0)

    if sys.argv[1] == "show":
        vol = Volume()
        hd = SmartData(hds)
	iface = Interface(ifaces) 
	parse(hd, vol, iface)
        show(hd, vol, iface)

