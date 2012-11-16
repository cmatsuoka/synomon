# -*- coding: utf-8 -*-

from pyrrd.graph import DEF, CDEF, VDEF, LINE, AREA, GPRINT
from pyrrd.graph import Graph as RRDGraph

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

    def cpu(self, c1, c2, c3, c5):
        def1 = self._def(vname='user'  , dsName='stat_user')
        def2 = self._def(vname='nice'  , dsName='stat_nice')
        def3 = self._def(vname='system', dsName='stat_system')
        def4 = self._def(vname='idle'  , dsName='stat_idle')
        def5 = self._def(vname='iowait', dsName='stat_iowait')
        def6 = self._def(vname='irq'   , dsName='stat_irq')
        def7 = self._def(vname='softirq', dsName='stat_softirq')
	cdef = CDEF(vname='all', rpn='user,nice,+,system,+,idle,+,iowait,+,irq,+,softirq,+')
        cdef1 = CDEF(vname='puser'  , rpn='100,user,*,all,/')
        cdef2 = CDEF(vname='pnice'  , rpn='100,nice,*,all,/')
        cdef3 = CDEF(vname='psystem', rpn='100,system,*,all,/')
        cdef5 = CDEF(vname='piowait', rpn='100,iowait,*,all,/')

	area1 = AREA(defObj=cdef1, color=c1, legend='User', stack=True)
	area2 = AREA(defObj=cdef2, color=c2, legend='Nice', stack=True)
	area3 = AREA(defObj=cdef3, color=c3, legend='System', stack=True)
	area5 = AREA(defObj=cdef5, color=c5, legend='IOwait', stack=True)

        self._data = self._data + [ def1, def2, def3, def4, def5, def6, def7,
                                    cdef, cdef1, cdef2, cdef3, cdef5, area3,
                                    area1, area2, area5 ]

    def hdtemp(self, hds):
        i = 0
        for hd in hds:
            name = "hd%d_temp" % (i)
            legend =  "HD%d temperature" % (i + 1)
            def1 = self._def(vname=name, dsName=name)
            line1 = LINE(defObj=def1, color=color1[i] + '40') 
            cdef1 = CDEF(vname=name + '_t', rpn="%s,3000,TREND" % (name))
            line2 = LINE(defObj=cdef1, color=color1[i], width=2, legend=legend)
            self._data = self._data + [ def1, line1, cdef1, line2 ]
            i = i + 1

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
        def1 = [ ]
        def2 = [ ]
        cdef = [ ]
        line = [ ]
	i = 0

        for v in vols:
            name_total = "vol%d_total" % (i)
            name_used  = "vol%d_used" % (i)

            def1.append(self._def(vname="v%dt" % (i), dsName=name_total))
            def2.append(self._def(vname="v%du" % (i), dsName=name_used))
            cdef.append(CDEF(vname="v%dp" % (i),
                             rpn="v%du,100,*,v%dt,/" % (i, i)))
	    line.append(LINE(defObj=cdef[i], color=color1[i], width=2,
                             legend=v[1]))

	    self._data = self._data + [ def1[i], def2[i], cdef[i], line[i] ]

            i = i + 1

    def day_graph(self, path, label, size=(0,0)):
	g = RRDGraph(path, start=-3600*24, end=-1, vertical_label=label)
        g.data.extend(self._data)
        if size[0] > 0:
            g.width = size[0]
        if size[1] > 0:
            g.height = size[1]
        #g.write(debug=True)
        g.write()

class Graph:
    def __init__(self, path, width=0, height=0):
        self._path = path
        self._width = width
        self._height = height
    
    def _set_size(self, width, height):
        size = [ self._width, self._height ]
        if width > 0:
            size[0] = width, 
        if height > 0:
            size[1] = height
        self._size = tuple(size) 

    def network(self, filename, width=0, height=0):
	''' Network I/O graph '''
	self._set_size(width, height)
	r = Report(self._path + '/network.rrd')
        r.area('eth0_rx', '#00c000', 'Network rx')
        r.line('eth0_tx', '#0000c0', 'Network tx')
	r.day_graph(filename, 'Bytes', self._size)

    def cpu(self, filename, width=0, height=0):
	''' CPU stats graph '''
	self._set_size(width, height)
	r = Report(self._path + '/stat.rrd')
        r.cpu('#00c000', '#c0c000', '#0000c0', '#c00000')
	r.day_graph(filename, 'Percentage', self._size)

    def load(self, filename, width=0, height=0):
	''' CPU load graph '''
	self._set_size(width, height)
	r = Report(self._path + '/load.rrd')
        r.area('load_15', '#00c000', '15 min')
        r.line('load_1', '#0000c0', '1 min')
	r.day_graph(filename, 'Active\ tasks', self._size)

    def memory(self, filename, width=0, height=0):
	''' Memory usage graph '''
	self._set_size(width, height)
	r = Report(self._path + '/memory.rrd')
	r.memory('#00c000', '#0000c0', '#00c0c0c0', '#c00000')
	r.day_graph(filename, 'KBytes', self._size)

    def hdtemp(self, hds, filename, width=0, height=0):
        ''' HD temperature graph '''
	self._set_size(width, height)
	r = Report(self._path + '/hds.rrd')
	r.hdtemp(hds)
	r.day_graph(filename, 'Celsius', self._size)

    def hdio(self, hds, filename, width=0, height=0):
        ''' HD I/O graph '''
	self._set_size(width, height)
	r = Report(self._path + '/hdio.rrd')
        i = 0
        for hd in hds:
            r.line("hd%d_reads"  % (i), color1[i], "HD%d reads"  % (i + 1))
            r.line("hd%d_writes" % (i), color2[i], "HD%d writes" % (i + 1))
            i = i + 1
	r.day_graph(filename, 'Sectors', self._size)

    def hdtime(self, hds, filename, width=0, height=0):
        ''' HD I/O graph '''
	self._set_size(width, height)
	r = Report(self._path + '/hdio.rrd')
        i = 0
        for hd in hds:
            r.line("hd%d_readtime"  % (i), color1[i], "HD%d read"  % (i + 1))
            r.line("hd%d_writetime" % (i), color2[i], "HD%d write" % (i + 1))
            i = i + 1
	r.day_graph(filename, 'Milliseconds', self._size)

    def volume(self, vols, filename, width=0, height=0):
        ''' Volume usage graph '''
	self._set_size(width, height)
	r = Report(self._path + '/volumes.rrd')
        r.volume(vols)
	r.day_graph(filename, 'Percent', self._size)

