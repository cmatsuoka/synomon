# -*- coding: utf-8 -*-

'''
Graph building class

This class encapsulates pyrrd graph building calls.
'''

from pyrrd.graph import DEF, CDEF, LINE, AREA
from pyrrd.graph import Graph as RRDGraph

COLOR1 = [ '#c00000', '#00c000', '#0000c0', '#c0c000', '#c08000',
           '#8000c0', '#00c0c0', '#c000c0', '#804000', '#408040' ]
COLOR2 = [ '#800080', '#008080', '#0080c0', '#00c080' ]

class _GraphBuilder:
    ''' Helpers to build a RRDtool graph using pyrrd calls '''
    def __init__(self, rrd_file):
        self._data = []
        self._rrd_file = rrd_file

    def _def(self, vname='vname', dsname='dsname'):
        ''' Wrapper for DEF using our RRD file '''
        return DEF(rrdfile=self._rrd_file, vname=vname, dsName=dsname)

    def line(self, name, color, legend):
        ''' Create RRDtool LINE definition '''
        def1 = self._def(vname=name, dsname=name)
        line1 = LINE(defObj=def1, color=color, legend=legend) 
        self._data = self._data + [ def1, line1 ]

    def area(self, name, color, legend):
        ''' Create RRDtool AREA definition '''
        def1 = self._def(vname=name, dsname=name)
        line1 = AREA(defObj=def1, color=color, legend=legend) 
        self._data = self._data + [ def1, line1 ]

    def cpu(self, color1, color2, color3, color5):
        ''' Create CPU stat graph elements '''
        def1 = self._def(vname='user'  , dsname='stat_user')
        def2 = self._def(vname='nice'  , dsname='stat_nice')
        def3 = self._def(vname='system', dsname='stat_system')
        def4 = self._def(vname='idle'  , dsname='stat_idle')
        def5 = self._def(vname='iowait', dsname='stat_iowait')
        def6 = self._def(vname='irq'   , dsname='stat_irq')
        def7 = self._def(vname='softirq', dsname='stat_softirq')
        cdef = CDEF(vname='all', rpn='user,nice,+,system,+,idle,+,' +
                          'iowait,+,irq,+,softirq,+')
        cdef1 = CDEF(vname='puser'  , rpn='100,user,*,all,/')
        cdef2 = CDEF(vname='pnice'  , rpn='100,nice,*,all,/')
        cdef3 = CDEF(vname='psystem', rpn='100,system,*,all,/')
        cdef5 = CDEF(vname='piowait', rpn='100,iowait,*,all,/')

        area1 = AREA(defObj=cdef1, color=color1, legend='User', stack=True)
        area2 = AREA(defObj=cdef2, color=color2, legend='Nice', stack=True)
        area3 = AREA(defObj=cdef3, color=color3, legend='System', stack=True)
        area5 = AREA(defObj=cdef5, color=color5, legend='IOwait', stack=True)

        self._data = self._data + [ def1, def2, def3, def4, def5, def6, def7,
                                    cdef, cdef1, cdef2, cdef3, cdef5, area3,
                                    area1, area2, area5 ]

    def hdtemp(self, hds):
        ''' Create HD temperature graph elements '''
        for i in range(len(hds)):
            name = "hd%d_temp" % (i)
            legend =  "HD%d temperature" % (i + 1)
            def1 = self._def(vname=name, dsname=name)
            line1 = LINE(defObj=def1, color=COLOR1[i] + '40') 
            cdef1 = CDEF(vname=name + '_t', rpn="%s,3000,TREND" % (name))
            line2 = LINE(defObj=cdef1, color=COLOR1[i], width=2, legend=legend)
            self._data = self._data + [ def1, line1, cdef1, line2 ]

    def memory(self, color1, color2, color3, color4):
        ''' Create memory usage graph elements '''
        def1 = self._def(vname='tot', dsname='mem_total')
        def2 = self._def(vname='fre', dsname='mem_free')
        def3 = self._def(vname='buf', dsname='mem_buffers')
        def4 = self._def(vname='cac', dsname='mem_cached')
        cdef1 = CDEF(vname='used', rpn='tot,fre,-,buf,-,cac,-')
        area1 = AREA(defObj=cdef1, color=color1, legend='Used', stack=True)
        area2 = AREA(defObj=def3, color=color2, legend='Buffers', stack=True)
        area3 = AREA(defObj=def4, color=color3, legend='Cached', stack=True)
        def5 = self._def(vname='swt', dsname='swap_total')
        def6 = self._def(vname='swf', dsname='swap_free')
        cdef2 = CDEF(vname='swap', rpn='swt,swf,-')
        line5 = LINE(defObj=cdef2, color=color4, legend='Swap')
        self._data = self._data + [ def1, def2, def3, def4, cdef1, area1,
                                    area2, area3, def5, def6, cdef2, line5 ]

    def volume(self, vols):
        ''' Create volume usage graph elements '''
        def1 = [ ]
        def2 = [ ]
        cdef = [ ]
        line = [ ]
        i = 0

        for vol in vols:
            name_total = 'vol%d_total' % (i)
            name_used  = 'vol%d_used' % (i)

            def1.append(self._def(vname='v%dt' % (i), dsname=name_total))
            def2.append(self._def(vname='v%du' % (i), dsname=name_used))
            cdef.append(CDEF(vname='v%dp' % (i),
                             rpn='v%du,100,*,v%dt,/' % (i, i)))
            line.append(LINE(defObj=cdef[i], color=COLOR1[i], width=2,
                             legend=vol[1]))

            self._data = self._data + [ def1[i], def2[i], cdef[i], line[i] ]

            i = i + 1

    def do_graph(self, path, label, view='', size=(0,0)):
        ''' Create the graph image file '''
        if path == '':
            raise Exception("Invalid filename")

        if view == 'y':
            start = 3600 * 24 * 365
        elif view == 'm':
            start = 3600 * 24 * 30
        elif view == 'w':
            start = 3600 * 24 * 7
        else:
            start = 3600 * 24

        print "Write image", path
        rrd_graph = RRDGraph(path, start=-start, end=-1, vertical_label=label)
        rrd_graph.data.extend(self._data)
        if size[0] > 0:
            rrd_graph.width = size[0]
        if size[1] > 0:
            rrd_graph.height = size[1]
        #rrd_graph.write(debug=True)
        rrd_graph.write()

class Graph:
    ''' Create graphs for data stored in RRDs '''
    def __init__(self, path, dest, width=0, height=0, view=''):
        self._path = path
        self._dest = dest
        self._width = width
        self._height = height
        self._view = view
        self._size = ()
        self._filename = ''
    
    def _set_size(self, width, height):
        ''' Set graph size '''
        size = [ self._width, self._height ]
        if width > 0:
            size[0] = width, 
        if height > 0:
            size[1] = height
        self._size = tuple(size) 

    def _set_filename(self, name, view):
        ''' Set image file name '''
        if view == '':
            view = self._view
        self._filename = self._dest + '/' + name + view + '.png'

    def router(self, filename, width=0, height=0, view=''):
        ''' Router traffic graph '''
        self._set_size(width, height)
        self._set_filename(filename, view)
        graph = _GraphBuilder(self._path + '/router.rrd')
        graph.area('rx', '#00c000', 'Network rx')
        graph.line('tx', '#0000c0', 'Network tx')
        graph.do_graph(self._filename, 'Bytes', self._view, self._size)

    def network(self, filename, width=0, height=0, view=''):
        ''' Network I/O graph '''
        self._set_size(width, height)
        self._set_filename(filename, view)
        graph = _GraphBuilder(self._path + '/network.rrd')
        graph.area('eth0_rx', '#00c000', 'Network rx')
        graph.line('eth0_tx', '#0000c0', 'Network tx')
        graph.do_graph(self._filename, 'Bytes', self._view, self._size)

    def cpu(self, filename, width=0, height=0, view=''):
        ''' CPU stats graph '''
        self._set_size(width, height)
        self._set_filename(filename, view)
        graph = _GraphBuilder(self._path + '/stat.rrd')
        graph.cpu('#00c000', '#c0c000', '#0000c0', '#c00000')
        graph.do_graph(self._filename, 'Percentage', self._view, self._size)

    def load(self, filename, width=0, height=0, view=''):
        ''' CPU load graph '''
        self._set_size(width, height)
        self._set_filename(filename, view)
        graph = _GraphBuilder(self._path + '/load.rrd')
        graph.area('load_15', '#00c000', '15 min')
        graph.line('load_1', '#0000c0', '1 min')
        graph.do_graph(self._filename, r'Active\ tasks', self._view, self._size)

    def memory(self, filename, width=0, height=0, view=''):
        ''' Memory usage graph '''
        self._set_size(width, height)
        self._set_filename(filename, view)
        graph = _GraphBuilder(self._path + '/memory.rrd')
        graph.memory('#00c000', '#0000c0', '#00c0c0c0', '#c00000')
        graph.do_graph(self._filename, 'KBytes', self._view, self._size)

    def hdtemp(self, hds, filename, width=0, height=0, view=''):
        ''' HD temperature graph '''
        self._set_size(width, height)
        self._set_filename(filename, view)
        graph = _GraphBuilder(self._path + '/hds.rrd')
        graph.hdtemp(hds)
        graph.do_graph(self._filename, 'Celsius', self._view, self._size)

    def hdio(self, hds, filename, width=0, height=0, view=''):
        ''' HD I/O graph '''
        self._set_size(width, height)
        self._set_filename(filename, view)
        graph = _GraphBuilder(self._path + '/hdio.rrd')
        for i in range(len(hds)):
            graph.line('hd%d_reads'  % (i), COLOR1[i], 'HD%d reads'  % (i + 1))
            graph.line('hd%d_writes' % (i), COLOR2[i], 'HD%d writes' % (i + 1))
        graph.do_graph(self._filename, 'Sectors', self._view, self._size)

    def hdtime(self, hds, filename, width=0, height=0, view=''):
        ''' HD I/O graph '''
        self._set_size(width, height)
        self._set_filename(filename, view)
        graph = _GraphBuilder(self._path + '/hdio.rrd')
        for i in range(len(hds)):
            graph.line('hd%d_readtime'  % (i), COLOR1[i],
                       'HD%d read'  % (i + 1))
            graph.line('hd%d_writetime' % (i), COLOR2[i],
                       'HD%d write' % (i + 1))
        graph.do_graph(self._filename, 'Milliseconds', self._view, self._size)

    def volume(self, vols, filename, width=0, height=0, view=''):
        ''' Volume usage graph '''
        self._set_size(width, height)
        self._set_filename(filename, view)
        graph = _GraphBuilder(self._path + '/volumes.rrd')
        graph.volume(vols)
        graph.do_graph(self._filename, 'Percent', self._view, self._size)

