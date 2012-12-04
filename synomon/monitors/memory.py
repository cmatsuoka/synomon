# -*- coding: utf-8 -*-

'''
Read memory information

Check total memory, free memory, buffers, caches, active, inactive and
swap information from /proc/meminfo.
'''

from ..monitor import Monitor, MONITOR
from ..graph import Graph, GRAPH
from ..rrd import Rrd

_NAME = 'memory'


class _MemMonitor(Monitor):
    def __init__(self, config):
        super(_MemMonitor, self).__init__(config, _NAME)

    def _parse(self):
        try:
            with open('/proc/meminfo') as f:
                cmd = f.read()
        except Exception, err:
            print '%s: %s\n' % (self.__class__.__name__, str(err))
            cmd = None

        t = ()
        for parm in [ 'MemTotal', 'MemFree', 'Buffers', 'Cached', 'Active',
                      'Inactive', 'SwapTotal', 'SwapFree' ]:
            if cmd == None:
                data = 0
            else:
                m = self._search('^' + parm + ':.* (\d+) ', cmd)
                data = int(m.group(1))
            t = t + (data,)
        self._data = t

    def _create(self):
        rrd = Rrd(self._rrd_name)
        for i in [ 'total', 'free', 'buffers', 'cached', 'active',
                   'inactive', 'swap_total', 'swap_free' ]:
            rrd.add_gauge(i)
        rrd.create()

    def show(self):
        self._parse()
        print 'Memory data:'
        print '    MemTotal  :', self._data[0]
        print '    MemFree   :', self._data[1]
        print '    Buffers   :', self._data[2]
        print '    Cached    :', self._data[3]
        print '    Active    :', self._data[4]
        print '    Inactive  :', self._data[5]
        print '    SwapTotal :', self._data[6]
        print '    SwapFree  :', self._data[7]
        print


class _MemGraph(Graph):
    def __init__(self, config):
        super(_MemGraph, self).__init__(config, _NAME, _NAME)
        self._set_config_colors([ '#00c000', '#0000c0',
                                  '#00c0c0c0', '#c00000' ])

    def graph(self, width=0, height=0, view=''):
        super(_MemGraph, self).graph(width, height, view)

        g = self._build_graph('Bytes')
        defs = g.defs([ 'total', 'free', 'buffers', 'cached' ])
        cdef1 = g.cdef('used', 'total,free,-,buffers,-,cached,-')
        g.area(cdef1, self._get_color(0), 'Used', stack=True)
        g.area(defs[2], self._get_color(1), 'Buffers', stack=True)
        g.area(defs[3], self._get_color(2), 'Cached', stack=True)
	defs = g.defs([ 'swap_total', 'swap_free' ])
        cdef2 = g.cdef('swap', 'swap_total,swap_free,-')
        g.line(cdef2, self._get_color(3), 'Swap')
        g.do_graph()


MONITOR[_NAME] = _MemMonitor
GRAPH[_NAME]   = _MemGraph, _NAME
