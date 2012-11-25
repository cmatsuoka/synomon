# -*- coding: utf-8 -*-

import subprocess
import re
import os

from .rrd import Rrd

class Monitor(object):
    def __init__(self, config, name):
        if name != None:
            self._name = name
        self._data = ()
        self._config = config
        self._rrd_name = config.get('Global', 'rrd_dir') + '/' + name + '.rrd'
    
    def _run_command(self, cmd):
        return subprocess.check_output(cmd.split())

    def _search(self, pattern, string):
        return re.search(pattern, string, re.MULTILINE)

    def _rrd_update(self, section):
        filename = self._config.get('Global', 'rrd_dir') + '/' + self._config.get(section, 'rrd')
        if not os.path.exists(filename):
            self.create(filename)
        Rrd(filename).update(self._data)

    def _parse(self):
        raise NotImplementedError

    def _create(self, filename):
        raise NotImplementedError

    def show(self):
        raise NotImplementedError

    def update(self):
        self._parse()
        if not os.path.exists(self._rrd_name):
            self._create()
        Rrd(self._rrd_name).update(self._data)


MONITOR = { }

def all():
    return MONITOR.keys()

def monitors(config):
    ret = [ MONITOR[i](config) for i in config.getlist('Global', 'monitors') ]
    if config.changed():
        config.write()
    return ret

