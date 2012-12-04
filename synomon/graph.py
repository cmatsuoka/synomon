# -*- coding: utf-8 -*-

'''
Graph building class

This class encapsulates pyrrd graph building calls.
'''

import synomon.config
from collections import defaultdict
from pyrrd.graph import DEF, CDEF, LINE, AREA
from pyrrd.graph import Graph as RRDGraph


class _GraphBuilder:
    ''' Helpers to build a RRDtool graph using pyrrd calls '''
    def __init__(self, rrd_file, filename, label, width, height, view):
        self._data = []
        self._rrd_file = rrd_file
        self._filename = filename
        self._label = label
        self._width = width
        self._height = height
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
        if self._width > 0:
            rrd_graph.width = self._width
        if self._height > 0:
            rrd_graph.height = self._height
        #rrd_graph.write(debug=True)
        rrd_graph.write()


class Graph(object):
    ''' Create graphs for data stored in RRDs '''

    _color1 = [ '#c00000', '#00c000', '#0000c0', '#c0c000', '#c08000',
                '#8000c0', '#00c0c0', '#c000c0', '#804000', '#408040' ]

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
        self._colors = self._color1

    def _get_config_colors(self, section):
        colors = self._config.getlist(section, 'colors')
        return [ '#' + i for i in colors ]

    def _set_config_colors(self, colors):
        clist = []
        for c in colors:
            if c[0] == '#':
                clist.append(c[1:])
            else:
                clist.append(c)

        section = 'Graph.' + self._gname
        if not self._config.has_option(section, 'colors'):
            self._config.add_option(section, 'colors', ','.join(clist))
    
    def _build_graph(self, label):

        # Set colors
        section = 'Graph.' + self._gname
        if self._config.has_option(section, 'colors'):
            self._colors = self._get_config_colors(section)

        return _GraphBuilder(self._rrd_name, self._filename, label,
                             self._width, self._height, self._view)

    def _get_color(self, index):
        i = index % len(self._colors)
        return self._colors[i]
    
    def monitor(self):
        return self._name

    def name(self):
        return self._gname

    def graph(self, width=0, height=0, view=None):
        w = h = 0

        # Set graph size
        if self._config.has_option('Graph', 'width'):
            w = self._config.getint('Graph', 'width')
        if self._config.has_option('Graph', 'height'):
            h = self._config.getint('Graph', 'height')

        # Set specific graph size
        section = 'Graph.' + self._gname
        if self._config.has_option(section, 'width'):
            w = self._config.getint(section, 'width')
        if self._config.has_option(section, 'height'):
            h = self._config.getint(section, 'height')

        # Parameter has precedence
        if width > 0: w = width
        if height > 0 : h = height

        self._width = w
        self._height = h
        self._view = view

        if view == None:
            view = ''
        else:
            view = '_' + view 
        self._filename = self._dest_dir + '/' + self._gname + view + '.png'


GRAPH = { }

def all():
    gm = defaultdict(list)
    for i in GRAPH.keys():
        gm[GRAPH[i][1]].append(i)
    return gm

def graphs(config):
    ret = [ GRAPH[i][0](config) for i in config.getlist('Global', 'graphs') ]
    if config.changed():
        config.write(warn=False)
    return ret
