#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
NAS monitor script

Configure directories for RRD files and HTML files in the variables below.
Volumes are in (block device, alias) format. If you plan to add more volumes
or hard disks reserve space for them in the CONF_MAX_* variables.
'''

import sys

from synomon.graph import Graph

import synomon.config
import synomon.monitor
from synomon.monitors import *


if __name__ == '__main__':

    config = synomon.config.Config()

    if len(sys.argv) < 2:
        print "Usage: %s [ list | show | update | report ]" % (sys.argv[0])
        sys.exit(0)

    if sys.argv[1] == 'list':
        print 'Available monitors and graphs:'
        gm = synomon.graph.all()
            
        for i in sorted(synomon.monitor.all()):
            sys.stdout.write('  %-10.10s: ' % (i))
            if (i in gm):
                print ', '.join(sorted(gm[i]))
            else:
                print '(no graphs defined)'

    elif sys.argv[1] == 'show':
        for i in synomon.monitor.monitors(config):
            i.show()

    elif sys.argv[1] == 'update':
        for i in synomon.monitor.monitors(config):
            i.update()

    elif sys.argv[1] == 'report':
        print 'Generating report...'

        if len(sys.argv) > 2:
            view = sys.argv[2]
        else:
            view = ''

        for i in synomon.graph.graphs(config):
            i.graph(height=150, width=480, view=view)

    else:
        print "Invalid command %s" % (sys.argv[1])
        sys.exit(1)

