# -*- coding: utf-8 -*-

'''
Get host load averages

Read /proc/loadavg to get 5 and 15 minute load average, 1 minute average
isn't used because monitor polling is done each 5 minutes.
'''

from ..monitor import Monitor, MONITOR
from ..graph import Graph, GRAPH
from ..rrd import Rrd

_NAME = 'load'


class _LoadMonitor(Monitor):
    def __init__(self, config):
        super(_LoadMonitor, self).__init__(config, _NAME)

    def _parse(self):
        try:
            with open("/proc/loadavg") as f:
                m = self._search("^[\d.]+ ([\d.]+) ([\d.]+) ", f.read())
                self._data = tuple(map(float, m.group(1, 2)))
        except:
            self._data = 0, 0, 0

    def _create(self):
        rrd = Rrd(self._rrd_name)
        rrd.add_gauge('load_5')
        rrd.add_gauge('load_15')
        rrd.create()

    def show(self):
        self._parse()
        print "CPU load:"
        print "    5m  average :", self._data[0]
        print "    15m average :", self._data[1]
        print


class _LoadGraph(Graph):
    def __init__(self, config):
        super(_LoadGraph, self).__init__(config, _NAME, _NAME)

    def graph(self, width=0, height=0, view=''):
        super(_LoadGraph, self).graph(width, height, view)

        g = self._build_graph(r'Active\ tasks')
        defs = g.defs([ 'load_15', 'load_5' ])
        g.area(defs[0], '#00c000', '15 min')
        g.line(defs[1], '#0000c0', '5 min')
        g.do_graph()


MONITOR[_NAME] = _LoadMonitor
GRAPH[_NAME]   = _LoadGraph
