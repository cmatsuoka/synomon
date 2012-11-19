# -*- coding: utf-8 -*-

import os
import sys
import ConfigParser

class Config:
    """
    Configuration file manager

    Locate, open and read configuration file options, creates a template
    if no configuration file is found (default is /opt/etc/monitor.conf)
    """
    def __init__(self):
        self._file = os.path.join('/opt/etc/monitor.conf')

        if not os.path.isfile(self._file):
            self._create_file()

        self._config = ConfigParser.ConfigParser()
        self._config.read(self._file)

    def get(self, section, option):
        """
        Get and return a given config field

        @param section: likely to be the monitor
        @param option: the field you want to retrieve from the config
        """
        return self._config.get(section, option)

    def getlist(self, section, option):
        return [ i.strip() for i in self.get(section, option).split(',') ]

    def getint(self, section, option):
        return self._config.getint(section, option)

    def items(self, section):
        return self._config.items(section)

    def _create_file(self):
        """Internal function to create a dummy config file if none is found"""

        config = ConfigParser.ConfigParser()
        config.add_section('Global')
        config.set('Global', 'rrd_dir', '/opt/var/lib/monitor')
        config.set('Global', 'dest_dir', '/volume1/web/stats/')
        config.set('Global', 'monitors', 'uptime,stat,load,memory,volume,hd,io,network')

        config.add_section('Uptime')
        config.set('Uptime', 'rrd', 'uptime.rrd')

        config.add_section('Stat')
        config.set('Stat', 'rrd', 'stat.rrd')

        config.add_section('Load')
        config.set('Load', 'rrd', 'load.rrd')

        config.add_section('Network')
        config.set('Network', 'rrd', 'network.rrd')
        config.set('Network', 'max_lan', '2')
        config.set('Network', 'ifaces', 'eth0')

        config.add_section('Disk')
        config.set('Disk', 'rrd', 'hds.rrd')
        config.set('Disk', 'max_hds', '2')
        config.set('Disk', 'hds', 'sda,sdb')

        config.add_section('DiskIO')
        config.set('DiskIO', 'rrd', 'hdio.rrd')

        config.add_section('Volumes')
        config.set('Volumes', 'rrd', 'volumes.rrd')
        config.set('Volumes', 'max_vols', '10')

        config.add_section('VolumeList')
        config.set('VolumeList', 'Sys', '/dev/md0')
        config.set('VolumeList', 'Vol1', '/dev/vg1/volume_1')
        config.set('VolumeList', 'Vol2', '/dev/vg1/volume_2')

        config.add_section('Tplink')
        config.set('Tplink', 'host', '192.168.1.1')
        config.set('Tplink', 'user', 'admin')
        config.set('Tplink', 'password', 'password')

        with open(self._file, 'w') as configfile:
            config.write(configfile)

        print '\nPlease edit your config file %s\n' % (self._file)
        sys.exit()
