# -*- coding: utf-8 -*-

'''
Gather traffic data from TP-Link wireless router

This module provides functionality to retrieve router traffic data from
the TP-Link WR542G router (firmare 4.0.1) by reading its HTML status page
since this device doesn't offer a management service.
'''
 
import re

from ..monitor import Monitor, MONITOR
from ..graph import Graph, GRAPH
from ..rrd import Rrd

_NAME = 'tplink'

class _TplinkMonitor(Monitor):
    def __init__(self, config):
        super(_TplinkMonitor, self).__init__(config, _NAME)

        if config.has_options('Tplink', [ 'host', 'user', 'password' ]):
            self._host = config.get('Tplink', 'host')
            self._user = config.get('Tplink', 'user')
            self._password = config.get('Tplink', 'password')
        else:
            config.add_option('Txplink', 'host', '192.168.1.1.')
            config.add_option('Txplink', 'user', 'admin')
            config.add_option('Txplink', 'password', 'password')

    def _parse(self):
        userdef = '%s:%s' % (self._user, self._password)
        try:
            cmd = self._run_command('curl -s --user ' + userdef + ' http://' +
                                    self._host + '/userRpm/StatusRpm.htm')
            m = re.search(r'var statistList = new Array\(\n(\d+), (\d+)', cmd)
            self._data = tuple(map(int, m.group(1, 2)))
        except:
            self._data = 0, 0

    def _create(self):
        rrd = Rrd(self._rrd_name)
        rrd.add_counter('rx')
        rrd.add_counter('tx')
        rrd.create()

    def show(self):
        self._parse()

        print "Router traffic:"
        print "    Received :", self._data[0]
        print "    Sent     :", self._data[1]
        print


class _TplinkGraph(Graph):
    def __init__(self, config):
        super(_TplinkGraph, self).__init__(config, _NAME)

    def graph(self, width=0, height=0, view=''):
        super(_TplinkGraph, self).graph(width, height, view)

        g = self._build_graph('Bytes')
        defs = g.defs([ 'rx', 'tx' ])
        g.area(defs[0], '#00c000', 'Network rx')
        g.line(defs[1], '#0000c0', 'Network tx')
        g.do_graph()


MONITOR[_NAME] = _TplinkMonitor
GRAPH[_NAME]   = _TplinkGraph
