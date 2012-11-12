import time

from pyrrd.rrd import DataSource, RRA, RRD
from pyrrd.graph import DEF, CDEF, VDEF, LINE, AREA, GPRINT
from pyrrd.graph import Graph

class Report:
    def __init__(self, rrd_file):
        self._data = []
        self._rrd_file = rrd_file

    def line(self, name, color, legend):
        def1 = DEF(rrdfile=self._rrd_file, vname=name, dsName=name)
        line1 = LINE(defObj=def1, color=color, legend=legend) 
	self._data = self._data + [ def1, line1 ]

    def area(self, name, color, legend):
        def1 = DEF(rrdfile=self._rrd_file, vname=name, dsName=name)
        line1 = AREA(defObj=def1, color=color, legend=legend) 
	self._data = self._data + [ def1, line1 ]

    def day_graph(self, path, label):
	now = int(time.time())
	time_day = 60 * 60 * 24
	g = Graph(path, start=now-time_day, end=now, vertical_label=label)
        g.data.extend(self._data)
        g.write(debug=True)

class Rrd:
    def __init__(self, rrd_file):
        self._ds = []
        self._rra = []
        self._rrd_file = rrd_file

    def _add_gauge(self, name):
        self._ds.append(DataSource(dsName=name, dsType='GAUGE', heartbeat=600))

    def _add_counter(self, name):
        self._ds.append(DataSource(dsName=name, dsType='COUNTER', heartbeat=600))
        
    def create(self, max_vols, max_hds, max_lan):
        # CPU load data
        for i in [ 'cpu_load1', 'cpu_load5', 'cpu_load15' ]:
            self._add_gauge(i)

        # Memory data
        for i in [ 'mem_total', 'mem_free', 'mem_buffers', 'mem_cached',
                   'mem_active', 'mem_inactive', 'swap_total', 'swap_free' ]:
            self._add_gauge(i)

        # Volume data
        self._add_gauge('sys_total')
        self._add_gauge('sys_used')

        for i in range(max_vols):
            vol = "vol%d_" % (i + 1)
            self._add_gauge(vol + "total")
            self._add_gauge(vol + "used")

        # Disk data
        for i in range(max_hds):
            hd = "sd%c_" % (ord('a') + i)
            self._add_gauge(hd + "temp")
            self._add_gauge(hd + "hours")
            self._add_gauge(hd + "starts")
            self._add_counter(hd + "reads")
            self._add_counter(hd + "readtime")
            self._add_counter(hd + "writes")
            self._add_counter(hd + "writetime")

        # Network
        for i in range(max_lan):
            lan = "eth%d_" % (i)
            self._add_counter(lan + "rx")
            self._add_counter(lan + "tx")

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

    def report(self):

	# CPU load graph
	r = Report(self._rrd_file)
        r.area('cpu_load15', '#00c000', '15 min')
        r.line('cpu_load5', '#0000c0', '5 min')
        r.line('cpu_load1', '#c00000', '1 min')
	r.day_graph('/volume1/web/bla.png', 'Active\ tasks')

        # HD temperature graph
	r = Report(self._rrd_file)
        r.line('sda_temp', '#c00000', 'HD1 temperature')
        r.line('sdb_temp', '#0000c0', 'HD2 temperature')
	r.day_graph('/volume1/web/bla2.png', 'Celsius')

        # HD I/O graph
	r = Report(self._rrd_file)
        r.line('sda_reads',  '#c00000', 'HD1 reads')
        r.line('sda_writes', '#0000c0', 'HD1 writes')
        r.line('sdb_reads',  '#c0c000', 'HD2 reads')
        r.line('sdb_writes', '#00c0c0', 'HD2 writes')
	r.day_graph('/volume1/web/bla3.png', 'Sectors')

