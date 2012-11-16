#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from synomon.monitor import *
from synomon.graph import Graph

conf_update_time = 300
conf_rrd_dir = "/opt/var/lib/monitor"
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

hds      = [ 'sda', 'sdb' ]
ifaces   = [ 'eth0' ]

max_hds  = 2
max_vols = 10
max_lan  = 1

#
#
#

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print "Usage: %s [ show | update | report ]" % (sys.argv[0])
        sys.exit(0)

    if sys.argv[1] == 'show':
        for i in [ UptimeMonitor(), StatMonitor(), LoadMonitor(), MemMonitor(),
                   VolMonitor(volumes, max_vols), HDMonitor(hds, max_hds),
                   IOMonitor(hds, max_hds), NetMonitor(ifaces, max_lan) ]:
            i.show()

    elif sys.argv[1] == 'update':
        for i in [ UptimeMonitor(), StatMonitor(), LoadMonitor(), MemMonitor(),
                   VolMonitor(volumes, max_vols), HDMonitor(hds, max_hds),
                   IOMonitor(hds, max_hds), NetMonitor(ifaces, max_lan) ]:
            i.update(conf_rrd_dir)

    elif sys.argv[1] == 'report':
        print 'Generating report...'
        graph = Graph(conf_rrd_dir, height=150)
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

