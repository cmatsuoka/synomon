#!/usr/bin/python

import subprocess
import sys
import re

conf_update_time = 300
conf_rrd_file = "/opt/etc/monitor.rrd"
conf_dest_dir = "/volume1/web/stats"
conf_filename = "index.html"

volumes = [ 1, 2, 3, 4, 5 ]
hds     = [ "sda", "sdb" ]
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

#
#
#

class Monitor:
    def parse(self):
        raise NotImplementedError

    def show(self):
        raise NotImplementedError

class VolumeMonitor(Monitor):
    def __init__(self):
        self._cmd = run_command("df -m")
	self._data = { }

    def parse(self, dev):
        m = search("^" + dev + "\s+(\d+)\s+(\d+)", self._cmd)
        self._data[dev] = tuple([int(i) for i in m.group(1, 2)])

    def show(self):
	print "Volume data:"
	for i in sorted(self._data.keys()):
            print "    %s:" % (i)
            print "        Total   : %d" % (self._data[i][0])
            print "        Used    : %d" % (self._data[i][1])
            print "        Percent : %4.1f%%" % (100.0 * self._data[i][1]
                                                 / self._data[i][0])
            print

class HDMonitor(Monitor):
    def __init__(self, hdlist):
	self._cmd = { }
	self._data = { }

	for hd in hdlist:
            self._cmd[hd] = run_command("smartctl -d ata -A /dev/" + hd)
	    self._data[hd] = { }

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

class IOMonitor(Monitor):
    def __init__(self, hdlist):
	self._line = { }
	self._data = { }

	for dev in hdlist:
	    try:
                f = open("/sys/block/" + dev + "/stat")
		self._line[dev] = [ int(i) for i in f.readline().split() ]
            except:
		self._line[dev] = [ 0 ] * 11


    def parse(self, dev):
        line = self._line[dev]
        self._data[dev] = line[2], line[3], line[6], line[7]

    def show(self):
	print "IO data:"
	for i in sorted(self._data.keys()):
            print "    %s:" % (i)
            print "        Sector reads  : %d" % (self._data[i][0])
            print "        Read time     : %d ms" % (self._data[i][1])
            print "        Sector writes : %d" % (self._data[i][2])
            print "        Write time    : %d ms" % (self._data[i][3])
            print
        pass

class NetMonitor(Monitor):
    def __init__(self, iflist):
        self._cmd = { }
        self._data = { }

        for i in iflist:
            self._cmd[i] = run_command("ifconfig " + i)

    def parse(self, iface):
        m = search("RX bytes:(\d+) .*TX bytes:(\d+)", self._cmd[iface])
        self._data[iface] = tuple([int(i) for i in m.group(1, 2)])

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

def parse(hd, vol, io, net):
    vol.parse("/dev/md0")
    
    for i in volumes:
        vol.parse("/dev/vg1/volume_%d" % (i))
    
    for i in hds:
        hd.parse(i, "Temperature_Celsius")
        hd.parse(i, "Power_On_Hours")
        hd.parse(i, "Start_Stop_Count")
        io.parse(i)

    for i in ifaces:
        net.parse(i)

def show(hd, vol, io, net):
    hd.show()
    vol.show()
    io.show()
    net.show()


if __name__ == "__main__":

    if len(sys.argv) < 2:
	print "Usage: %s [ show | update | report ]" % (sys.argv[0])
	sys.exit(0)

    if sys.argv[1] == "show":
        vol = VolumeMonitor()
        hd  = HDMonitor(hds)
        io  = IOMonitor(hds)
	net = NetMonitor(ifaces) 
	parse(hd, vol, io, net)
        show(hd, vol, io, net)

