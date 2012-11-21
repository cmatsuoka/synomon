# -*- coding: utf-8 -*-

'''
Read memory information

Check total memory, free memory, buffers, caches, active, inactive and
swap information from /proc/meminfo.
'''

import re

from ..monitor import Monitor, MONITOR
from ..rrd import Rrd

class _MemMonitor(Monitor):
    def __init__(self, config):
        super(_MemMonitor, self).__init__(config, 'memory')

    def _parse(self):
        try:
            with open('/proc/meminfo') as f:
                cmd = f.read()
        except:
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
        for i in [ 'mem_total', 'mem_free', 'mem_buffers', 'mem_cached',
                   'mem_active', 'mem_inactive', 'swap_total', 'swap_free' ]:
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


MONITOR['memory'] = _MemMonitor
