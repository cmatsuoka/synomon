# -*- coding: utf-8 -*-

'''
Read volume information

Check logical volume usage data.
'''

import re

from ..monitor import Monitor, MONITOR
from ..rrd import Rrd


class _VolMonitor(Monitor):
    def __init__(self, config):
        super(_VolMonitor, self).__init__(config, 'volumes')

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


MONITOR['volumes'] = _VolMonitor
