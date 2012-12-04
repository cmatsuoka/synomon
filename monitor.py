#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
NAS monitor script

Configure directories for RRD files and HTML files in the variables below.
Volumes are in (block device, alias) format. If you plan to add more volumes
or hard disks reserve space for them in the CONF_MAX_* variables.
'''

import sys
import argparse
import synomon.config
import synomon.monitor
from synomon.monitors import *

def cmd_list(args, config):
    print 'Available monitors and graphs:'
    gm = synomon.graph.all()
            
    for i in sorted(synomon.monitor.all()):
        sys.stdout.write('  %-10.10s: ' % (i))
        if (i in gm):
            print ', '.join(sorted(gm[i]))
        else:
            print '(no graphs defined)'

def cmd_show(args, config):
    for i in synomon.monitor.monitors(config):
        i.show()

def cmd_update(args, config):
    for i in synomon.monitor.monitors(config):
        i.update()

def cmd_report(args, config):
    print 'Generating report...'
    view = args.range;
    for i in synomon.graph.graphs(config):
        i.graph(view=view)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--config-file', metavar='file',
                  default='/opt/etc/monitor.conf',
                  help='configuration file to use')
    subparser = parser.add_subparsers()

    list_parser = subparser.add_parser('list',
                  help='list all available monitors and graphs')
    list_parser.set_defaults(func=cmd_list)

    show_parser = subparser.add_parser('show',
                  help='show values retrieved by monitors')
    show_parser.set_defaults(func=cmd_show)

    update_parser = subparser.add_parser('update', help='update database')
    update_parser.set_defaults(func=cmd_update)

    report_parser = subparser.add_parser('report', help='generate graphs')
    report_parser.add_argument('-w', '--weekly', dest='range', const='w',
                  action='store_const', help='weekly graph')
    report_parser.add_argument('-m', '--monthly', dest='range', const='m',
                  action='store_const', help='monthly graph')
    report_parser.add_argument('-y', '--yearly', dest='range', const='y',
                  action='store_const', help='yearly graph')
    report_parser.set_defaults(func=cmd_report)

    args = parser.parse_args()

    config = synomon.config.Config(args.config_file)
    args.func(args, config)
