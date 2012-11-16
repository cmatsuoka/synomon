#!/usr/bin/env python

import sys
import os

from synomon.monitor import *
from synomon.rrd import *
from synomon.graph import Graph

conf_update_time = 300
conf_rrd_file = "/opt/var/lib/monitor.rrd"
conf_dest_dir = "/volume1/web/stats"

volumes  = [
    ('/dev/md0', 'Sys'),
    ('/dev/vg1/volume_1', 'Vol1'),
    ('/dev/vg1/volume_2', 'Vol2'),
    ('/dev/vg1/volume_3', 'Vol3'),
    ('/dev/vg1/volume_4', 'Vol4'),
    ('/dev/vg1/volume_5', 'Vol5'),
    ('/dev/vg2/volume_6', 'Vol6')
]

hds      = [ "sda", "sdb" ]
lan      = [ "eth0" ]

max_hds  = 2
max_vols = 10
max_lan  = 1

#
#
#

def parse(up, cnt, cpu, mem, hd, vol, io, net):
    up.parse()
    cnt.parse()
    cpu.parse()

    for i in [ "MemTotal", "MemFree", "Buffers", "Cached", "Active",
               "Inactive", "SwapTotal", "SwapFree" ]:
        mem.parse(i)

    for i in volumes:
        vol.parse(i[0])
    
    for i in hds:
        hd.parse(i, "Temperature_Celsius")
        hd.parse(i, "Power_On_Hours")
        hd.parse(i, "Start_Stop_Count")
        io.parse(i)

    for i in lan:
        net.parse(i)

def show(up, cnt, cpu, mem, hd, vol, io, net):
    up.show()
    cnt.show()
    cpu.show()
    mem.show()
    net.show()
    hd.show()
    io.show()
    vol.show()

def get_data(up, cnt, cpu, mem, hd, vol, io, net):
    # Uptime data
    t = up.get_data()

    # Jiffy counter data
    t = t + cnt.get_data()

    # CPU load data
    t = t + cpu.get_data()

    # Memory data
    t = t + mem.get_data()

    # Volume data
    temp = [ 0 ] * (2 * max_vols)
    i = 0
    for v in volumes:
        temp[i], temp[i + 1] = vol.get_data(v[0])
        i = i + 2
    t = t + tuple(temp)

    # Disk data
    temp = [ 0 ] * (7 * max_hds)
    for dev in hds:
        i = ord(dev[2]) - ord('a')
	if not 0 <= i < max_hds:
	    raise ValueError
        j = i * 7
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
        up  = UptimeMonitor()
        cnt = StatMonitor()
        cpu = LoadMonitor()
        mem = MemMonitor()
        vol = VolMonitor()
        hd  = HDMonitor(hds)
        io  = IOMonitor(hds)
        net = NetMonitor(lan) 
        parse(up, cnt, cpu, mem, hd, vol, io, net)
        show(up, cnt, cpu, mem, hd, vol, io, net)

    elif sys.argv[1] == "update":
        rrd = Rrd(conf_rrd_file)

	if not os.path.exists(conf_rrd_file):
            rrd.create(max_vols, max_hds, max_lan)

        up  = UptimeMonitor()
        cnt = StatMonitor()
        cpu = LoadMonitor()
        mem = MemMonitor()
        vol = VolMonitor()
        hd  = HDMonitor(hds)
        io  = IOMonitor(hds)
        net = NetMonitor(lan) 
        parse(up, cnt, cpu, mem, hd, vol, io, net)

	data = get_data(up, cnt, cpu, mem, hd, vol, io, net)
        rrd.update(data)

    elif sys.argv[1] == "report":
        print "Generating report..."
        graph = Graph(conf_rrd_file, height=150)
        graph.network(conf_dest_dir + '/g0.png')
        graph.cpu(conf_dest_dir + '/g1.png')
        graph.load(conf_dest_dir + '/g2.png')
        graph.memory(conf_dest_dir + '/g3.png')
        graph.hdtemp(hds, conf_dest_dir + '/g4.png')
        graph.hdio(hds, conf_dest_dir + '/g5.png')
        graph.hdtime(hds, conf_dest_dir + '/g6.png')
        graph.volume(volumes, conf_dest_dir + '/g7.png')
        
    else:
        print "Invalid command %s" % (sys.argv[1])
        sys.exit(1)
