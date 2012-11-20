# -*- coding: utf-8 -*-

'''
Get hard disk I/O data

Read number of sectors read/written in hard disks and read/write time
from /sys/block.
'''

import re

from ..monitor import Monitor, MONITORS
from ..rrd import Rrd


class _IOMonitor(Monitor):
    def __init__(self, config):
        super(_IOMonitor, self).__init__(config, 'hdio')

        if config.has_options('Hd', [ 'hds', 'max_hds' ]):
            self._hds = config.getlist('Hd', 'hds')
            self._max_hds = config.getint('Hd', 'max_hds')
        else:
            config.add_option('Hd', 'hds', 'sda,sdb')
            config.add_option('Hd', 'max_hds', 2)

        self._cmd = { }

        for hd in self._hds:
            try:
                with open('/sys/block/' + hd + '/stat') as f:
                    self._cmd[hd] = map(int, f.readline().split())
            except:
                self._cmd[hd] = [ 0 ] * 11

    def _parse(self):
        temp = [ 0 ] * (4 * self._max_hds)
        i = 0
        for hd in self._hds:
            line = self._cmd[hd]
            temp[i] = line[2]
            temp[i + 1] = line[2]
            temp[i + 2] = line[6]
            temp[i + 3] = line[7]
            i = i + 4

        self._data = temp

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

MONITORS['hdio'] = _IOMonitor
