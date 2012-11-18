# -*- coding: utf-8 -*-

'''
RRD access

This module encapsulates RRD creation and updates using pyrrd. 
'''

import time

from pyrrd.rrd import DataSource, RRA, RRD

class Rrd:
    ''' RRD database access '''
    def __init__(self, rrd_file):
        self._ds = []
        self._rra = []
        self._rrd_file = rrd_file

    def add_gauge(self, name):
        ''' Create a DS with type GAUGE '''
        self._ds.append(DataSource(dsName=name, dsType='GAUGE', heartbeat=600))

    # From http://oss.oetiker.ch/rrdtool/doc/rrdcreate.en.html
    #
    # If you cannot tolerate ever mistaking the occasional counter reset for a
    # legitimate counter wrap, and would prefer "Unknowns" for all legitimate
    # counter wraps and resets, always use DERIVE with min=0.

    def add_counter(self, name):
        ''' Create a DS with type COUNTER '''
        self._ds.append(DataSource(dsName=name, dsType='DERIVE', minval=0,
                                                heartbeat=600))
        
    def create(self):
        ''' Create the RRD '''
        # 5 minute average for daily view
        self._rra.append(RRA(cf='AVERAGE', xff=0.5, steps=1, rows=288))

        # 30 minute average for weekly view
        self._rra.append(RRA(cf='AVERAGE', xff=0.5, steps=6, rows=336))
        self._rra.append(RRA(cf='MAX',     xff=0.5, steps=6, rows=336))
        self._rra.append(RRA(cf='MIN',     xff=0.5, steps=6, rows=336))

        # 2 hour average for monthly view
        self._rra.append(RRA(cf='AVERAGE', xff=0.5, steps=24, rows=360))
        self._rra.append(RRA(cf='MAX',     xff=0.5, steps=24, rows=360))
        self._rra.append(RRA(cf='MIN',     xff=0.5, steps=24, rows=360))

        # 24 hour average for yearly view
        self._rra.append(RRA(cf='AVERAGE', xff=0.5, steps=288, rows=365))
        self._rra.append(RRA(cf='MAX',     xff=0.5, steps=288, rows=365))
        self._rra.append(RRA(cf='MIN',     xff=0.5, steps=288, rows=365))

        print "Create %s" % (self._rrd_file)
        my_rrd = RRD(self._rrd_file, ds=self._ds, rra=self._rra)
        my_rrd.create()

    def update(self, data):
        ''' Update the RRD '''
        my_rrd = RRD(self._rrd_file)
        my_rrd.bufferValue(time.time(), *data)
        my_rrd.update()
