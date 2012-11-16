# -*- coding: utf-8 -*-

import time

from pyrrd.rrd import DataSource, RRA, RRD

class Rrd:
    def __init__(self, rrd_file):
        self._ds = []
        self._rra = []
        self._rrd_file = rrd_file

    def add_gauge(self, name):
        self._ds.append(DataSource(dsName=name, dsType='GAUGE', heartbeat=600))

    def add_counter(self, name):
        self._ds.append(DataSource(dsName=name, dsType='COUNTER', heartbeat=600))
        
    def create(self):
        # 5 minute average for daily view (5 day log)
        self._rra.append(RRA(cf='AVERAGE', xff=0.5, steps=1, rows=1440))

        # 30 minute average for monthly view (30 day log)
        self._rra.append(RRA(cf='AVERAGE', xff=0.5, steps=6, rows=1440))

        # 6 hour average for yearly view (360 day log)
        self._rra.append(RRA(cf='AVERAGE', xff=0.5, steps=72, rows=1440))

        print "Create %s" % (self._rrd_file)

        my_rrd = RRD(self._rrd_file, ds=self._ds, rra=self._rra);
        my_rrd.create()

    def update(self, data):
        my_rrd = RRD(self._rrd_file)
        my_rrd.bufferValue(time.time(), *data)
        my_rrd.update()
