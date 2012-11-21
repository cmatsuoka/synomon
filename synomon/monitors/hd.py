# -*- coding: utf-8 -*-

'''
Get hard disk information

Read hard disk temperature, power-on hours and start/stop counters.
'''

import re

from ..monitor import Monitor, MONITOR
from ..rrd import Rrd


class _HDMonitor(Monitor):
    def __init__(self, config):
        super(_HDMonitor, self).__init__(config, 'hd')

        if config.has_options('Hd', [ 'hds', 'max_hds' ]):
            self._hds = config.getlist('Hd', 'hds')
            self._max_hds = config.getint('Hd', 'max_hds')
        else:
            config.add_option('Hd', 'hds', 'sda,sdb')
            config.add_option('Hd', 'max_hds', 2)

    def _parse(self):
        cmd = { }
        for hd in self._hds:
            try:
                cmd[hd] = self._run_command('smartctl -d ata -A /dev/' + hd)
            except:
                cmd[hd] = None

        temp = [ 0 ] * (3 * self._max_hds)
        i = 0
        for hd in self._hds:
            if cmd[hd] == None:
                data = [ 0, 0, 0 ] 
            else:
                data = [ ]
                for parm in [ 'Temperature_Celsius', 'Power_On_Hours',
                              'Start_Stop_Count' ]:
                   m = self._search(parm + ' .* (\d+)( \(.*\))?$', cmd[hd])
                   data.append(int(m.group(1)))
            temp[i], temp[i + 1], temp[i + 2] = data
            i = i + 3

        self._data = tuple(temp)

    def _create(self):
        rrd = Rrd(self._rrd_name)
        for i in range(self._max_hds):
            hd = "hd%d_" % i
            rrd.add_gauge(hd + 'temp')
            rrd.add_gauge(hd + 'hours')
            rrd.add_gauge(hd + 'starts')
        rrd.create()

    def show(self):
        self._parse()
        print 'Hard disk data:'
        i = 0
        for hd in self._hds:
            print "    %s:" % (hd)
            print '        Temperature      :', self._data[i], '°C' 
            print '        Power-on hours   :', self._data[i + 1]
            print '        Start/stop count :', self._data[i + 2]
            print
            i = i + 3

MONITOR['hd'] = _HDMonitor
