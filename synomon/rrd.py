import time

from pyrrd.rrd import DataSource, RRA, RRD
from pyrrd.graph import DEF, CDEF, VDEF, LINE, AREA, GPRINT
from pyrrd.graph import Graph

color1 = [ '#c00000', '#00c000', '#0000c0', '#c0c000', '#c08000',
           '#8000c0', '#00c0c0', '#c000c0', '#804000', '#408040' ]
color2 = [ '#800080', '#008080', '#0080c0', '#00c080' ]

class Report:
    def __init__(self, rrd_file):
        self._data = []
        self._rrd_file = rrd_file

    def _def(self, vname='vname', dsName='dsName'):
        return DEF(rrdfile=self._rrd_file, vname=vname, dsName=dsName)

    def line(self, name, color, legend):
        def1 = self._def(vname=name, dsName=name)
        line1 = LINE(defObj=def1, color=color, legend=legend) 
	self._data = self._data + [ def1, line1 ]

    def area(self, name, color, legend):
        def1 = self._def(vname=name, dsName=name)
        line1 = AREA(defObj=def1, color=color, legend=legend) 
	self._data = self._data + [ def1, line1 ]

    def memory(self, c1, c2, c3, c4):
        def1 = self._def(vname='tot', dsName='mem_total')
        def2 = self._def(vname='fre', dsName='mem_free')
        def3 = self._def(vname='buf', dsName='mem_buffers')
        def4 = self._def(vname='cac', dsName='mem_cached')
        cdef1 = CDEF(vname='used', rpn='tot,fre,-,buf,-,cac,-')
	area1 = AREA(defObj=cdef1, color=c1, legend='Used', stack=True)
	area2 = AREA(defObj=def3, color=c2, legend='Buffers', stack=True)
	area3 = AREA(defObj=def4, color=c3, legend='Cached', stack=True)
        def5 = self._def(vname='swt', dsName='swap_total')
        def6 = self._def(vname='swf', dsName='swap_free')
        cdef2 = CDEF(vname='swap', rpn='swt,swf,-')
	line5 = LINE(defObj=cdef2, color=c4, legend='Swap')
	self._data = self._data + [ def1, def2, def3, def4, cdef1, area1,
                                    area2, area3, def5, def6, cdef2, line5 ]

    def volume(self, vols):
        def1 = [ self._def(vname='st', dsName='sys_total') ]
        def2 = [ self._def(vname='su', dsName='sys_used') ]
        cdef = [ CDEF(vname='sp', rpn='su,100,*,st,/') ]
	line = [ LINE(defObj=cdef[0], color=color1[0], legend='Sys') ]

        for i in vols:
            name_total = "vol%d_total" % (i)
            name_used  = "vol%d_used" % (i)

            def1.append(self._def(vname="v%dt" % (i), dsName=name_total))
            def2.append(self._def(vname="v%du" % (i), dsName=name_used))
            cdef.append(CDEF(vname="v%dp" % (i),
                             rpn="v%du,100,*,v%dt,/" % (i, i)))
	    line.append(LINE(defObj=cdef[i], color=color1[i],
                             legend="Vol%d" % (i)))

        for i in [ 0 ] + vols:
	    self._data = self._data + [ def1[i], def2[i], cdef[i], line[i] ]


    def day_graph(self, path, label):
	now = int(time.time())
	time_day = 60 * 60 * 24
	g = Graph(path, start=now-time_day, end=now, vertical_label=label)
        g.data.extend(self._data)
        #g.write(debug=True)
        g.write()


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
        # Stat data
        for i in [ 'stat_user', 'stat_nice', 'stat_system', 'stat_idle',
                   'stat_iowait', 'stat_irq', 'stat_softirq' ]:
            self._add_counter(i)

        # CPU load data
        for i in [ 'load_1', 'load_5', 'load_15' ]:
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

    def report(self, dest, hds, vols, lan):

	# Network I/O 
	r = Report(self._rrd_file)
        r.area('eth0_rx', '#00c000', 'Network rx')
        r.line('eth0_tx', '#0000c0', 'Network tx')
	r.day_graph(dest + '/g0.png', 'Bytes')

	# CPU load graph
	r = Report(self._rrd_file)
        r.area('load_15', '#00c000', '15 min')
        r.line('load_1', '#0000c0', '1 min')
	r.day_graph(dest + '/g1.png', 'Active\ tasks')

	# Memory usage graph
	r = Report(self._rrd_file)
	r.memory('#00c000', '#0000c0', '#00c0c0', '#c00000')
	r.day_graph(dest + '/g2.png', 'KBytes')

        # HD temperature graph
	r = Report(self._rrd_file)
        for i in hds:
            j = ord(i[2]) - ord('a')
            r.line("%s_temp" % (i), color1[j], "HD%d temperature" % (j + 1))
	r.day_graph(dest + '/g3.png', 'Celsius')

        # HD I/O graph
	r = Report(self._rrd_file)

        for i in hds:
            j = ord(i[2]) - ord('a')
            r.line("%s_reads"  % (i), color1[j], "HD%d reads"  % (j + 1))
            r.line("%s_writes" % (i), color2[j], "HD%d writes" % (j + 1))
	r.day_graph(dest + '/g4.png', 'Sectors')

        # Volume usage graph
	r = Report(self._rrd_file)
        r.volume(vols)
	r.day_graph(dest + '/g5.png', 'Percent')

