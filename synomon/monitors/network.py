# -*- coding: utf-8 -*-

'''
Read network tx/rx values

Read /proc/loadavg to get 5 and 15 minute load average, 1 minute average
isn't used because monitor polling is done each 5 minutes.
'''

from ..monitor import Monitor, MONITOR
from ..graph import Graph, GRAPH
from ..rrd import Rrd

_NAME = 'network'


class _NetMonitor(Monitor):
    def __init__(self, config):
        super(_NetMonitor, self).__init__(config, _NAME)

        if config.has_options('Network', [ 'ifaces', 'max_lan' ]):
            self._ifaces = config.getlist('Network', 'ifaces')
            self._max_lan = config.getint('Network', 'max_lan')
        else:
            config.add_option('Network', 'ifaces', 'eth0')
            config.add_option('Network', 'max_lan', 1)


    def _parse(self):
        cmd = { }
        for i in self._ifaces:
            cmd[i] = self._run_command("ifconfig " + i)

        temp = [ 0 ] * (2 * self._max_lan)
        i = 0
        for iface in self._ifaces:
            m = self._search("RX bytes:(\d+) .*TX bytes:(\d+)", cmd[iface])
            temp[i], temp[i + 1] = tuple(map(int, m.group(1, 2)))
            i += 2
        self._data = temp

    def _create(self):
        rrd = Rrd(self._rrd_name)
        for i in range(self._max_lan):
            lan = "eth%d_" % (i)
            rrd.add_counter(lan + "rx")
            rrd.add_counter(lan + "tx")
        rrd.create()

    def show(self):
        self._parse()
        print "Network interface data:"
        i = 0
        for iface in self._ifaces:
            print "    %s:" % (iface)
            print "        Rx bytes : %d" % (self._data[i])
            print "        Tx bytes : %d" % (self._data[i + 1])
            print
            i = i + 2


class _NetGraph(Graph):
    def __init__(self, config):
        super(_NetGraph, self).__init__(config, _NAME, _NAME)

    def graph(self, width=0, height=0, view=''):
        super(_NetGraph, self).graph(width, height, view)

        g = self._build_graph('Bytes')
        defs = g.defs([ 'eth0_rx', 'eth0_tx' ])
        g.area(defs[0], '#00c000', 'Network rx')
        g.line(defs[1], '#0000c0', 'Network tx')
        g.do_graph()


MONITOR[_NAME] = _NetMonitor
GRAPH[_NAME]   = _NetGraph
