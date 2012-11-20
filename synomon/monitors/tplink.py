# -*- coding: utf-8 -*-

'''
Gather traffic data from TP-Link wireless router

This module provides functionality to retrieve router traffic data from
the TP-Link WR542G router (firmare 4.0.1) by reading its HTML status page
since this device doesn't offer a management service.
'''
 
import re

from ..monitor import Monitor, MONITORS
from ..rrd import Rrd


class _TplinkMonitor(Monitor):
    def __init__(self, config):
        super(_TplinkMonitor, self).__init__(config, 'tplink')

        if config.has_options('Tplink', [ 'host', 'user', 'password' ]):
            host = config.get('Tplink', 'host')
            user = config.get('Tplink', 'user')
            password = config.get('Tplink', 'password')
        else:
            config.add_option('Txplink', 'host', '192.168.1.1.')
            config.add_option('Txplink', 'user', 'admin')
            config.add_option('Txplink', 'password', 'password')

        userdef = '%s:%s' % (user, password)
        self._cmd = self._run_command('curl -s --user ' + userdef + ' http://' +
                                      host + '/userRpm/StatusRpm.htm')

    def _parse(self):
        if self._cmd == None:
            self._data = 0, 0
        else:
            m = re.search(r'var statistList = new Array\(\n(\d+), (\d+)',
                          self._cmd)
            self._data = tuple(map(int, m.group(1, 2)))

    def _create(self):
        rrd = Rrd(self._rrd_name)
        rrd.add_counter('rx')
        rrd.add_counter('tx')
        rrd.create()

    def show(self):
        self._parse()

        print "Router traffic:"
        print "    Received :", self._data[0]
        print "    Sent     :", self._data[1]
        print


MONITORS['tplink'] = _TplinkMonitor
