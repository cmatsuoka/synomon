#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
NAS monitor script

Configure directories for RRD files and HTML files in the variables below.
Volumes are in (block device, alias) format. If you plan to add more volumes
or hard disks reserve space for them in the CONF_MAX_* variables.
'''

import sys

from synomon.monitor import UptimeMonitor, StatMonitor, LoadMonitor, MemMonitor
from synomon.monitor import VolMonitor, HDMonitor, IOMonitor, NetMonitor
from synomon.tplink import RouterMonitor
from synomon.graph import Graph

CONF_RRD_DIR   = "/opt/var/lib/monitor"
CONF_DEST_DIR  = "/volume1/web/stats"

CONF_VOLUMES   = [
    ('/dev/md0', 'Sys'),
    ('/dev/vg1/volume_1', 'Vol1'),
    ('/dev/vg1/volume_2', 'Vol2'),
    ('/dev/vg1/volume_3', 'Vol3'),
    ('/dev/vg1/volume_4', 'Vol4'),
    ('/dev/vg1/volume_5', 'Vol5'),
    ('/dev/vg2/volume_6', 'Vol6')
]

CONF_HDS      = [ 'sda', 'sdb' ]
CONF_IFACES   = [ 'eth0' ]

CONF_MAX_HDS  = 2
CONF_MAX_VOLS = 10
CONF_MAX_LAN  = 1

# FIXME: don't hardcode stuff

def all_monitors():
    return [ RouterMonitor('address', 'username:password'),
             UptimeMonitor(), StatMonitor(), LoadMonitor(), MemMonitor(),
             VolMonitor(CONF_VOLUMES, CONF_MAX_VOLS),
             HDMonitor(CONF_HDS, CONF_MAX_HDS),
             IOMonitor(CONF_HDS, CONF_MAX_HDS),
             NetMonitor(CONF_IFACES, CONF_MAX_LAN) ]


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print "Usage: %s [ show | update | report ]" % (sys.argv[0])
        sys.exit(0)

    if sys.argv[1] == 'show':
        for i in all_monitors():
            i.show()

    elif sys.argv[1] == 'update':
        for i in all_monitors():
            i.update(CONF_RRD_DIR)

    elif sys.argv[1] == 'report':
        print 'Generating report...'

        if len(sys.argv) > 2:
            view = sys.argv[2]
        else:
            view = ''

        GRAPH = Graph(CONF_RRD_DIR, CONF_DEST_DIR, height=150, width=480,
                      view=view)
        GRAPH.router('g8')
        GRAPH.network('g0')
        GRAPH.cpu('g1')
        GRAPH.load('g2')
        GRAPH.memory('g3')
        GRAPH.hdtemp(CONF_HDS, 'g4')
        GRAPH.hdio(CONF_HDS, 'g5')
        #GRAPH.hdtime(CONF_HDS, 'g6')
        GRAPH.volume(CONF_VOLUMES, 'g7')
        
    else:
        print "Invalid command %s" % (sys.argv[1])
        sys.exit(1)

