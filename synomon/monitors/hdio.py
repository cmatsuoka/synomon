# -*- coding: utf-8 -*-

'''
Get hard disk I/O data

Read number of sectors read/written in hard disks and read/write time
from /sys/block.
'''

from ..monitor import Monitor, MONITOR
from ..graph import Graph, GRAPH
from ..rrd import Rrd

_NAME = 'hdio'


class _IOMonitor(Monitor):
    def __init__(self, config):
        super(_IOMonitor, self).__init__(config, _NAME)

        if config.has_options('Hd', [ 'hds', 'max_hds' ]):
            self._hds = config.getlist('Hd', 'hds')
            self._max_hds = config.getint('Hd', 'max_hds')
        else:
            config.add_option('Hd', 'hds', 'sda,sdb')
            config.add_option('Hd', 'max_hds', '2')

    def _parse(self):
        cmd = { }
        for hd in self._hds:
            try:
                with open('/sys/block/' + hd + '/stat') as f:
                    cmd[hd] = map(int, f.readline().split())
            except:
                cmd[hd] = [ 0 ] * 11

        temp = [ 0 ] * (4 * self._max_hds)
        i = 0
        for hd in self._hds:
            temp[i] = cmd[hd][2]
            temp[i + 1] = cmd[hd][2]
            temp[i + 2] = cmd[hd][6]
            temp[i + 3] = cmd[hd][7]
            i = i + 4

        self._data = tuple(temp)

    def _create(self):
        rrd = Rrd(self._rrd_name)
        for i in range(self._max_hds):
            hd = "hd%d_" % i
            rrd.add_counter(hd + 'reads')
            rrd.add_counter(hd + 'readtime')
            rrd.add_counter(hd + 'writes')
            rrd.add_counter(hd + 'writetime')
        rrd.create()

    def show(self):
        self._parse()
        print 'Hard disk I/O data:'
        i = 0
        for hd in self._hds:
            print "    %s:" % (hd)
            print '        Sectors read     :', self._data[i    ]
            print '        Read time        :', self._data[i + 1], 'ms'
            print '        Sectors written  :', self._data[i + 2]
            print '        Write time       :', self._data[i + 3], 'ms'
            print
            i = i + 4


class _IOGraph(Graph):
    def __init__(self, config):
        super(_IOGraph, self).__init__(config, _NAME, _NAME)
        self._set_config_colors([ '#c00000', '#00c000', '#800080', '#008080' ])

    def graph(self, width=0, height=0, view=''):
        super(_IOGraph, self).graph(width, height, view)

        hds = self._config.getlist('Hd', 'hds')

        g = self._build_graph('Sectors')
        for i in range(len(hds)):
            g.line(g.ddef('hd%d_reads'  % (i)), self._get_color(i * 2),
                          'HD%d reads'  % (i + 1))
            g.line(g.ddef('hd%d_writes' % (i)), self._get_color(i * 2 + 1),
                          'HD%d writes' % (i + 1))
        g.do_graph()


class _TimeGraph(Graph):
    def __init__(self, config):
        super(_TimeGraph, self).__init__(config, _NAME, _NAME + '.time')
        self._set_config_colors([ '#c00000', '#00c000', '#800080', '#008080' ])

    def graph(self, width=0, height=0, view=''):
        super(_TimeGraph, self).graph(width, height, view)

        hds = self._config.getlist('Hd', 'hds')

        g = self._build_graph('Milliseconds')
        for i in range(len(hds)):
            g.line(g.ddef('hd%d_readtime'  % (i)), self._get_color(i * 2),
                          'HD%d read'  % (i + 1))
            g.line(g.ddef('hd%d_writetime' % (i)), self._get_color(i * 2 + 1),
                          'HD%d write' % (i + 1))
        g.do_graph()


MONITOR[_NAME]         = _IOMonitor
GRAPH[_NAME]           = _IOGraph, _NAME
GRAPH[_NAME + '.time'] = _TimeGraph, _NAME
