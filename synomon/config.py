# -*- coding: utf-8 -*-

import os
import sys
import ConfigParser
from collections import defaultdict

class Config:
    """
    Configuration file manager

    Locate, open and read configuration file options, creates a template
    if no configuration file is found (default is /opt/etc/monitor.conf)
    """
    def __init__(self, configfile):
        self._file = configfile
        self._config = ConfigParser.ConfigParser()
        self._config.optionxform = str

        if not os.path.isfile(self._file):
           self._config.add_section('Global')
           self._config.set('Global', 'rrd_dir', '/opt/var/lib/monitor')
           self._config.set('Global', 'dest_dir', '/volume1/web/stats/')
           self._config.set('Global', 'monitors',
                            'uptime,cpu,load,memory,volumes,hd,hdio,network')
           self._config.set('Global', 'graphs',
                            'cpu,load,memory,volumes,hd.temp,hdio,network')
           self._config.add_section('Graph')
           self._config.set('Graph', 'width', '480')
           self._config.set('Graph', 'height', '150')
        else:
           self._config.read(self._file)

        self._sections = set(self._config.sections())
	self._options = defaultdict(set)
        for i in self._sections:
            self._options[i] = set(self._opt_list(self._config.items(i)))

    def _opt_list(self, list):
        return [ i[0] for i in list ]

    def changed(self):
        diff = set(self._config.sections()) - self._sections
	if diff:
            for i in diff:
                print 'Added section:', i
            return True
        for i in self._sections:
            if self._options[i] != set(self._opt_list(self._config.items(i))):
                return True
        return False

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

    def has_option(self, section, option):
        return self._config.has_option(section, option)

    def has_options(self, section, values):
        for i in values:
            if not self._config.has_option(section, i):
                return False
        return True

    def has_section(self, section):
        return self._config.has_section(section)

    def add_option(self, section, option, value):
        if not self._config.has_section(section):
            self._config.add_section(section)
        if not self._config.has_option(section, option):
            self._config.set(section, option, value)

    def add_section(self, section):
        self._config.add_section(section)

    def set(self, section, option, value):
        return self._config.set(section, option, value)

    def _create_file(self):
        """Internal function to create a dummy config file if none is found"""

    def write(self, warn=True):
        with open(self._file, 'w') as configfile:
            self._config.write(configfile)

        if warn:
            print '\nPlease edit the configuration file %s\n' % (self._file)
            sys.exit()

