#!/usr/bin/python

import subprocess
import sys
import re
import time
import os
import glob

from pyrrd.rrd import DataSource, RRA, RRD
from pyrrd.graph import DEF, CDEF, VDEF, LINE, AREA, GPRINT
from pyrrd.graph import Graph

conf_update_time = 300
conf_rrd_file = "/opt/etc/monitor.rrd"
conf_dest_dir = "/volume1/web/stats"
conf_filename = "index.html"

volumes  = [ 1, 2, 3, 4, 5, 6 ]
hds      = [ "sda", "sdb" ]
lan      = [ "eth0" ]

max_hds  = 2
max_vols = 10
max_lan  = 1

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

    def get_data(self):
        raise NotImplementedError

class MemMonitor(Monitor):
    def __init__(self):
        self._data = { }
        try:
            with open("/proc/meminfo") as f:
                self._cmd = f.read()
        except:
            self._cmd = None

    def parse(self, parm):
        if self._cmd == None:
            self._data[parm] = 0
        else:
            m = search("^" + parm + ":.* (\d+) ", self._cmd)
            self._data[parm] = int(m.group(1))

    def show(self):
        print "Memory data:"
        for i in sorted(self._data.keys()):
            print "    %-10.10s: %d kB" % (i, self._data[i])
        print

    def get_data(self):
        t = ()
        for i in [ "MemTotal", "MemFree", "Buffers", "Cached", "Active",
                   "Inactive", "SwapTotal", "SwapFree" ]:
            t = t + (self._data[i],)
        return t

class VolMonitor(Monitor):
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

    def get_data(self, dev):
        return self._data[dev]

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
            m = search(parm + " .* (\d+)( \(.*\))?$", self._cmd[hd])
            self._data[hd][parm] = int(m.group(1))

    def show(self):
        print "Hard disk data:"
        for i in sorted(self._data.keys()):
            print "    %s:" % (i)
            for j in self._data[i].keys():
                print "        %-20.20s: %d" % (j, self._data[i][j])
            print

    def get_data(self, hd):
        return self._data[hd]['Temperature_Celsius']

class IOMonitor(Monitor):
    def __init__(self, hdlist):
        self._line = { }
        self._data = { }

        for dev in hdlist:
            try:
                with open("/sys/block/" + dev + "/stat") as f:
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

    def get_data(self, dev):
        return self._data[dev]

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

    def get_data(self, iface):
        return self._data[iface]

#
#
#

class Rrd:
    def __init__(self):
        self._ds = []
        self._rra = []

    def _add_gauge(self, name):
        self._ds.append(DataSource(dsName=name, dsType='GAUGE', heartbeat=600))

    def _add_counter(self, name):
        self._ds.append(DataSource(dsName=name, dsType='COUNTER', heartbeat=600))
        
    def create(self):
        # Memory data
        for i in [ 'mem_total', 'mem_free', 'mem_buffers', 'mem_cached',
                   'mem_active', 'mem_inactive', 'swap_total', 'swap_free' ]:
            self._add_gauge(i)

        # Volume data
        self._add_gauge('sys_total')
        self._add_gauge('sys_used')

        for i in range(max_vols):
            vol = "vol%d_" % (i + 1)
            self._add_gauge(vol + "total")
            self._add_gauge(vol + "used")

        # Disk data
        for i in range(max_hds):
            hd = "sd%c_" % (ord('a') + i)
            self._add_gauge(hd + "temp")
            self._add_counter(hd + "reads")
            self._add_counter(hd + "readtime")
            self._add_counter(hd + "writes")
            self._add_counter(hd + "writetime")

        # Network
        for i in range(max_lan):
            lan = "eth%d_" % (i)
            self._add_counter(lan + "rx")
            self._add_counter(lan + "tx")

	self._rra.append(RRA(cf='AVERAGE', xff=0.5, steps=1, rows=10))
	self._rra.append(RRA(cf='AVERAGE', xff=0.5, steps=6, rows=10))

	my_rrd = RRD(conf_rrd_file, ds=self._ds, rra=self._rra);
	my_rrd.create()

    def update(self, data):
        my_rrd = RRD(conf_rrd_file)
        my_rrd.bufferValue(time.time(), *data)
	my_rrd.update()

    def report(self):
        def1 = DEF(rrdfile=conf_rrd_file, vname='mem', dsName='mem_total')
        line1 = LINE(value=100, color='#990000', legend='Maximum Allowed')

	g = Graph("/volume1/web/bla.png", vertical_label='km/h')
        g.data.extend([def1, cdef1, line1])
        g.write(debug=True)

#
#
#

def parse(mem, hd, vol, io, net):
    for i in [ "MemTotal", "MemFree", "Buffers", "Cached", "Active",
               "Inactive", "SwapTotal", "SwapFree" ]:
        mem.parse(i)

    vol.parse("/dev/md0")
    
    for i in volumes:
        path=glob.glob("/dev/vg*/volume_%d" % (i))
        vol.parse(path[0])
    
    for i in hds:
        hd.parse(i, "Temperature_Celsius")
        hd.parse(i, "Power_On_Hours")
        hd.parse(i, "Start_Stop_Count")
        io.parse(i)

    for i in lan:
        net.parse(i)

def show(mem, hd, vol, io, net):
    mem.show()
    net.show()
    hd.show()
    io.show()
    vol.show()

def get_data(mem, hd, vol, io, net):
    # Memory data
    t = mem.get_data()

    # Volume data
    temp = [ 0 ] * (2 * (max_vols + 1))
    temp[0], temp[1] = vol.get_data("/dev/md0")
    for i in volumes:
        temp[i * 2], temp[i * 2 + 1] = vol.get_data("/dev/vg1/volume_%d" % (i))
    t = t + tuple(temp)

    # Disk data
    temp = [ 0 ] * (5 * max_hds)
    for dev in hds:
        i = ord(dev[2]) - ord('a')
	if not 0 <= i < max_hds:
	    raise ValueError
        temp[i * 5] = hd.get_data(dev)
        temp[i * 5 + 1], temp[i * 5 + 2], temp[i * 5 + 3], temp[i * 5 + 4] = io.get_data(dev)
    t = t + tuple(temp)

    # Network
    temp = [ 0 ] * (2 * max_lan)
    for dev in lan:
        i = ord(dev[3]) - ord('0')
	if not 0 <= i < max_lan:
	    raise ValueError
        temp[i * 2], temp[i * 2 + 1] = net.get_data(dev)
    t = t + tuple(temp)

    return t


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print "Usage: %s [ show | update | report ]" % (sys.argv[0])
        sys.exit(0)

    if sys.argv[1] == "show":
        mem = MemMonitor()
        vol = VolMonitor()
        hd  = HDMonitor(hds)
        io  = IOMonitor(hds)
        net = NetMonitor(lan) 
        parse(mem, hd, vol, io, net)
        show(mem, hd, vol, io, net)

    elif sys.argv[1] == "update":
        rrd = Rrd()

	if not os.path.exists(conf_rrd_file):
            rrd.create()

        mem = MemMonitor()
        vol = VolMonitor()
        hd  = HDMonitor(hds)
        io  = IOMonitor(hds)
        net = NetMonitor(lan) 
        parse(mem, hd, vol, io, net)

	data = get_data(mem, hd, vol, io, net)
        rrd.update(data)

    elif sys.argv[1] == "report":
        rrd = Rrd()
        rrd.report()
        
