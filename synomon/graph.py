# -*- coding: utf-8 -*-

'''
Graph building class

This class encapsulates pyrrd graph building calls.
'''

from pyrrd.graph import DEF, CDEF, LINE, AREA
from pyrrd.graph import Graph as RRDGraph


class _GraphBuilder:
    ''' Helpers to build a RRDtool graph using pyrrd calls '''
    def __init__(self, rrd_file, filename, label, size, view):
        self._data = []
        self._rrd_file = rrd_file
        self._filename = filename
        self._label = label
        self._size = size
        self._view = view

    def ddef(self, name):
        ''' Wrapper for DEF using our RRD file '''
        def1 = DEF(rrdfile=self._rrd_file, vname=name, dsName=name)
        self._data = self._data + [ def1 ]
        return def1

    def defs(self, names):
        return map(self.ddef, names)

    def cdef(self, name, rpn):
        cdef1 = CDEF(vname=name, rpn=rpn)
        self._data = self._data + [ cdef1 ]
        return cdef1

    def line(self, defobj, color, legend, width=1):
        ''' Create RRDtool LINE definition '''
        line1 = LINE(defObj=defobj, color=color, legend=legend, width=width) 
        self._data = self._data + [ line1 ]

    def area(self, defobj, color, legend, stack=False):
        ''' Create RRDtool AREA definition '''
        area1 = AREA(defObj=defobj, color=color, legend=legend, stack=stack) 
        self._data = self._data + [ area1 ]

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
                             legend=vol[0]))

            self._data = self._data + [ def1[i], def2[i], cdef[i], line[i] ]

            i = i + 1

    def do_graph(self):
        ''' Create the graph image file '''
        if self._filename == '':
            raise Exception("Invalid filename")

        if self._view == 'y':
            start = 3600 * 24 * 365
        elif self._view == 'm':
            start = 3600 * 24 * 30
        elif self._view == 'w':
            start = 3600 * 24 * 7
        else:
            start = 3600 * 24

        print "Write image", self._filename
        rrd_graph = RRDGraph(self._filename, start=-start, end=-1,
                             vertical_label=self._label)
        rrd_graph.data.extend(self._data)
        if self._size[0] > 0:
            rrd_graph.width = self._size[0]
        if self._size[1] > 0:
            rrd_graph.height = self._size[1]
        #rrd_graph.write(debug=True)
        rrd_graph.write()

class Graph(object):
    ''' Create graphs for data stored in RRDs '''

    _color1 = [ '#c00000', '#00c000', '#0000c0', '#c0c000', '#c08000',
           '#8000c0', '#00c0c0', '#c000c0', '#804000', '#408040' ]
    _color2 = [ '#800080', '#008080', '#0080c0', '#00c080' ]

    def __init__(self, config, name, gname, width=0, height=0):
        self._config = config
        self._name = name
        self._gname = gname
        self._width = width
        self._height = height
        self._dest_dir = config.get('Global', 'dest_dir')
        self._rrd_name = config.get('Global', 'rrd_dir') + '/' + name + '.rrd'
        self._view = ''
        self._size = ()
    
    def _set_size(self, width, height):
        ''' Set graph size '''
        size = [ self._width, self._height ]
        if width > 0:
            size[0] = width
        if height > 0:
            size[1] = height
        self._size = tuple(size) 

    def graph(self, width, height, view):
        self._set_size(width, height)
        self._view = view
        if view != '':
            view = '-' + view 
        self._filename = self._dest_dir + '/' + self._gname + view + '.png'

    def _build_graph(self, label):
        return _GraphBuilder(self._rrd_name, self._filename, label,
                             self._size, self._view)

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

GRAPH = { }

def graphs(config):
    return [ GRAPH[i](config) for i in config.getlist('Global', 'graphs') ]
