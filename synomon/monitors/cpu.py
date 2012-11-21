# -*- coding: utf-8 -*-

'''
Read CPU usage information

This module reads CPU counters information from /proc/stat.
'''

from ..monitor import Monitor, MONITOR
from ..graph import Graph, GRAPH
from ..rrd import Rrd

_NAME = 'cpu'


class _CpuMonitor(Monitor):
    def __init__(self, config):
        super(_CpuMonitor, self).__init__(config, _NAME)

    def _parse(self):
        try:
            with open("/proc/stat") as f:
                m = self._search('cpu\s+(\d+) (\d+) (\d+) (\d+) (\d+) ' +
                                 '(\d+) (\d+)', f.readline())
                self._data = tuple(map(int, m.group(1, 2, 3, 4, 5, 6, 7)))
        except:
            self._data = 0, 0, 0, 0, 0, 0, 0

    def _create(self):
        rrd = Rrd(self._rrd_name)
        for i in [ 'user', 'nice', 'system', 'idle',
                   'iowait', 'irq', 'softirq' ]:
            rrd.add_counter(i)
        rrd.create()

    def show(self):
        self._parse()
        print 'CPU stats:'
        print '    User    :', self._data[0]
        print '    Nice    :', self._data[1]
        print '    System  :', self._data[2]
        print '    Idle    :', self._data[3]
        print '    IOwait  :', self._data[4]
        print '    IRQ     :', self._data[5]
        print '    Softirq :', self._data[6]
        print


class _CpuGraph(Graph):
    def __init__(self, config):
        super(_CpuGraph, self).__init__(config, _NAME, _NAME)

    def graph(self, width=0, height=0, view=''):
        super(_CpuGraph, self).graph(width, height, view)

        g = self._build_graph('Percentage')
        g.defs([ 'user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq' ])
        g.cdef('all', 'user,nice,+,system,+,idle,+,iowait,+,irq,+,softirq,+')
        cdef1 = g.cdef('puser'  , '100,user,*,all,/')
        cdef2 = g.cdef('pnice'  , '100,nice,*,all,/')
        cdef3 = g.cdef('psystem', '100,system,*,all,/')
        cdef4 = g.cdef('piowait', '100,iowait,*,all,/')
        g.area(cdef1, '#00c000', 'User', True)
        g.area(cdef2, '#c0c000', 'Nice', True)
        g.area(cdef3, '#0000c0', 'System', True)
        g.area(cdef4, '#c00000', 'IOwait', True)
        g.do_graph()


MONITOR[_NAME] = _CpuMonitor
GRAPH[_NAME]   = _CpuGraph
