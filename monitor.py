#!/usr/bin/env python

import sys
import os
import glob

from synomon.monitor import *
from synomon.rrd import *

conf_update_time = 300
conf_rrd_file = "/opt/var/lib/monitor.rrd"
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

def parse(cpu, mem, hd, vol, io, net):
    cpu.parse()

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

def show(cpu, mem, hd, vol, io, net):
    cpu.show()
    mem.show()
    net.show()
    hd.show()
    io.show()
    vol.show()

def get_data(cpu, mem, hd, vol, io, net):
    # CPU load data
    t = cpu.get_data()

    # Memory data
    t = t + mem.get_data()

    # Volume data
    temp = [ 0 ] * (2 * (max_vols + 1))
    temp[0], temp[1] = vol.get_data("/dev/md0")
    for i in volumes:
        path = glob.glob("/dev/vg*/volume_%d" % (i))
        temp[i * 2], temp[i * 2 + 1] = vol.get_data(path[0])
    t = t + tuple(temp)

    # Disk data
    temp = [ 0 ] * (7 * max_hds)
    for dev in hds:
        i = ord(dev[2]) - ord('a')
	if not 0 <= i < max_hds:
	    raise ValueError
        j = i * 5
        temp[j    ], temp[j + 1], temp[j + 2] = hd.get_data(dev)
        temp[j + 3], temp[j + 4], temp[j + 5], temp[j + 6] = io.get_data(dev)
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
        cpu = CPUMonitor()
        mem = MemMonitor()
        vol = VolMonitor()
        hd  = HDMonitor(hds)
        io  = IOMonitor(hds)
        net = NetMonitor(lan) 
        parse(cpu, mem, hd, vol, io, net)
        show(cpu, mem, hd, vol, io, net)

    elif sys.argv[1] == "update":
        rrd = Rrd(conf_rrd_file)

	if not os.path.exists(conf_rrd_file):
            rrd.create(max_vols, max_hds, max_lan)

        cpu = CPUMonitor()
        mem = MemMonitor()
        vol = VolMonitor()
        hd  = HDMonitor(hds)
        io  = IOMonitor(hds)
        net = NetMonitor(lan) 
        parse(cpu, mem, hd, vol, io, net)

	data = get_data(cpu, mem, hd, vol, io, net)
        rrd.update(data)

    elif sys.argv[1] == "report":
        rrd = Rrd(conf_rrd_file)
        rrd.report()
        
    else:
        print "Invalid command %s" % (sys.argv[1])
        sys.exit(1)
