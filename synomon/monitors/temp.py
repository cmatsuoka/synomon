# -*- coding: utf-8 -*-

'''
Read RDing TEMPer1V1 temperature sensor information

This module reads temperature information using usb.core. Sensor reading code
by Lance R. Vick, http://bb10.com/python-pyusb-user/2012-02/msg00005.html
'''

from ..monitor import Monitor, MONITOR
from ..graph import Graph, GRAPH
from ..rrd import Rrd

import usb.core

_NAME = 'temp'


class _Temp:
    def __init__(self, scale=1.0, offset=0.0):
        self.dev = usb.core.find(idVendor=0x0c45,idProduct=0x7401)
        self._scale = scale
        self._offset = offset

        #if dev.is_kernel_driver_active(1):
        try:
            self.dev.detach_kernel_driver(1)
        except:
            pass

        self.dev.set_configuration()

    def get(self):
        cmd = [0x01, 0x80, 0x33, 0x01, 0x00, 0x00, 0x00, 0x00]
        request = '' . join([chr(x) for x in cmd])
        self.dev.ctrl_transfer(0x21, 9, 0x200, 0x1, request, 8)
        raw = self.dev.read(0x82, 8, 1, 500)
        temp = (raw[3] + 256 * raw[2]) * 125.0 / 32000
        return temp * self._scale + self._offset


class _TempMonitor(Monitor):
    def __init__(self, config, name=_NAME):
        super(_TempMonitor, self).__init__(config, name)

        # Calibration
        self._scale = 1
        self._offset = 0

    def _parse(self):
        temp = _Temp(self._scale, self._offset)
        self._data = [ temp.get() ]

    def _create(self):
        rrd = Rrd(self._rrd_name)
        rrd.add_counter('temp')
        rrd.create()

    def show(self):
        self._parse()
        print 'Temperature :', self._data[0]
        print


class _TempGraph(Graph):
    def __init__(self, config):
        super(_TempGraph, self).__init__(config, _NAME, _NAME)
        self._set_config_colors([ '#0000c0' ])

    def graph(self, width=0, height=0, view=''):
        super(_TempGraph, self).graph(width, height, view)

        g = self._build_graph('Temperature')
        defs = g.defs([ 'temp' ])
        g.line(defs[0], self._get_color(0), 'temp')
        g.do_graph()


MONITOR[_NAME] = _TempMonitor
GRAPH[_NAME]   = _TempGraph, _NAME

