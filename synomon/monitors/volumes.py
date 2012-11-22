# -*- coding: utf-8 -*-

'''
Read volume information

Check logical volume usage data.
'''

from ..monitor import Monitor, MONITOR
from ..graph import Graph, GRAPH
from ..rrd import Rrd

_NAME = 'volumes'


class _VolMonitor(Monitor):
    def __init__(self, config):
        super(_VolMonitor, self).__init__(config, _NAME)

        if config.has_option('Volumes', 'max_vols'):
            self._max_vols = config.getint('Volumes', 'max_vols')
        else:
            config.add_option('Volumes', 'max_vols', 10)

        if config.has_section('VolumeList'):
	    self._volumes = config.items('VolumeList')
        else:
            config.add_option('VolumeList', 'sys', '/dev/md0')
            config.add_option('VolumeList', 'vol1', '/dev/vg1/volume_1')
            config.add_option('VolumeList', 'vol2', '/dev/vg1/volume_2')

    def _parse(self):
        temp = [ 0 ] * (2 * self._max_vols)
        try:
            cmd = self._run_command('df -m')
            i = 0
            for v in self._volumes:
                m = self._search('^' + v[1] + '\s+(\d+)\s+(\d+)', cmd)
                temp[i], temp[i + 1] = tuple(map(int, m.group(1, 2)))
                i = i + 2
        except:
            pass

        self._data = temp

    def _create(self):
        rrd = Rrd(self._rrd_name)
        for i in range(self._max_vols):
            vol = "vol%d_" % (i)
            rrd.add_gauge(vol + 'total')
            rrd.add_gauge(vol + 'used')
        rrd.create()

    def show(self):
        self._parse()
        print "Volume data:"
        i = 0
        for v in self._volumes:
            print "    %s [%s]:" % (v[1], v[0])
            print "        Total   : %d" % (self._data[i])
            print "        Used    : %d" % (self._data[i + 1])
            print "        Percent : %4.1f%%" % (100.0 * self._data[i + 1]
                                                 / self._data[i])
            print
            i = i + 2


    def volume(self, vols):
        ''' Create volume usage graph elements '''
        def1 = [ ]
        def2 = [ ]
        cdef = [ ]
        line = [ ]
        i = 0


class _VolGraph(Graph):
    def __init__(self, config):
        super(_VolGraph, self).__init__(config, _NAME, _NAME)

    def graph(self, width=0, height=0, view=''):
        super(_VolGraph, self).graph(width, height, view)

        vols = self._config.items('VolumeList')

        g = self._build_graph('Percentage')
        i = 0
        for vol in vols:
            total = 'vol%d_total' % (i)
            used  = 'vol%d_used' % (i)
            g.defs([ total, used ])
            cdef = g.cdef('v%dp' % (i), '%s,100,*,%s,/' % (total, used))
            g.line(cdef, self._color1[i], vol[0], width=2)
            i = i + 1
        g.do_graph()


MONITOR[_NAME] = _VolMonitor
GRAPH[_NAME]   = _VolGraph
