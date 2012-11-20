# -*- coding: utf-8 -*-

'''
Get host load averages

Read /proc/loadavg to get 5 and 15 minute load average, 1 minute average
isn't used because monitor polling is done each 5 minutes.
'''

import re

from ..monitor import Monitor, MONITORS
from ..rrd import Rrd


class _LoadMonitor(Monitor):
    def __init__(self, config):
        super(_LoadMonitor, self).__init__(config, 'load')
        try:
            with open("/proc/loadavg") as f:
                self._cmd = f.read()
        except:
            self._cmd = None

    def _parse(self):
        if self._cmd == None:
            self._data = 0, 0, 0
        else:
            m = self._search("^[\d.]+ ([\d.]+) ([\d.]+) ", self._cmd)
            self._data = tuple(map(float, m.group(1, 2)))

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


MONITORS['load'] = _LoadMonitor
