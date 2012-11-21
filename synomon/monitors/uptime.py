# -*- coding: utf-8 -*-

'''
Read uptime information

This module reads uptime seconds and idle seconds from /proc/uptime.
'''

import re

from ..monitor import Monitor, MONITORS
from ..config import Config
from ..rrd import Rrd


class _UptimeMonitor(Monitor):
    def __init__(self, config):
        super(_UptimeMonitor, self).__init__(config, 'uptime')

    def _parse(self):
        try:
            with open("/proc/uptime") as f:
                m = self._search("^([\d]+)\.\d+ ([\d]+)\.", f.read())
                self._data = tuple(map(int, m.group(1, 2)))
        except:
            self._data = 0, 0

    def _create(self):
        rrd = Rrd(self._rrd_name)
        rrd.add_counter('uptime')
        rrd.add_counter('idle')
        rrd.create()

    def show(self):
        self._parse()
        print "Uptime:"
        print "    Uptime seconds :", self._data[0]
        print "    Idle seconds   :", self._data[1]
        print

MONITORS['uptime'] = _UptimeMonitor
