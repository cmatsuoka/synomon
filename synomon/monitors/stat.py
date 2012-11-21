# -*- coding: utf-8 -*-

'''
Read CPU usage information

This module reads CPU counters information from /proc/stat.
'''

import re

from ..monitor import Monitor, MONITORS
from ..config import Config
from ..rrd import Rrd


class _StatMonitor(Monitor):
    def __init__(self, config):
        super(_StatMonitor, self).__init__(config, 'stat')

    def _parse(self):
        try:
            with open("/proc/stat") as f:
                m = self._search('cpu\s+(\d+) (\d+) (\d+) (\d+) (\d+) ' +
                                 '(\d+) (\d+)', r.readline())
                self._data = tuple(map(int, m.group(1, 2, 3, 4, 5, 6, 7)))
        except:
            self._data = 0, 0, 0, 0, 0, 0, 0

    def _create(self):
        rrd = Rrd(self._rrd_name)
        for i in [ 'stat_user', 'stat_nice', 'stat_system', 'stat_idle',
                   'stat_iowait', 'stat_irq', 'stat_softirq' ]:
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


MONITORS['stat'] = _StatMonitor
