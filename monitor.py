#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
NAS monitor script

Configure directories for RRD files and HTML files in the variables below.
Volumes are in (block device, alias) format. If you plan to add more volumes
or hard disks reserve space for them in the CONF_MAX_* variables.
'''

import sys

from synomon.config import Config
from synomon.graph import Graph

import synomon.monitor
import synomon.tplink


if __name__ == '__main__':

    config = Config()

    if len(sys.argv) < 2:
        print "Usage: %s [ show | update | report ]" % (sys.argv[0])
        sys.exit(0)

    if sys.argv[1] == 'show':
        for i in synomon.monitor.monitors(config):
            i.show()

    elif sys.argv[1] == 'update':
        for i in synomon.monitor.monitors(config):
            i.update(config.get('Global', 'rrd_dir'))

    elif sys.argv[1] == 'report':
        print 'Generating report...'

        if len(sys.argv) > 2:
            view = sys.argv[2]
        else:
            view = ''

        GRAPH = Graph(config, height=150, width=480, view=view)
        GRAPH.router('g8')
        GRAPH.network('g0')
        GRAPH.cpu('g1')
        GRAPH.load('g2')
        GRAPH.memory('g3')
        GRAPH.hdtemp(config.getlist('Disk', 'hds'), 'g4')
        GRAPH.hdio(config.getlist('Disk', 'hds'), 'g5')
        #GRAPH.hdtime(config.get_list('Disk', 'hds', 'g6')
        GRAPH.volume(config.items('VolumeList'), 'g7')
        
    else:
        print "Invalid command %s" % (sys.argv[1])
        sys.exit(1)

