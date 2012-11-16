# -*- coding: utf-8 -*-

import subprocess
import re
import os

from rrd import *

class Monitor:
    def _run_command(self, cmd):
        try:
            return subprocess.check_output(cmd.split())
        except:
            return None

    def _search(self, pattern, string):
        return re.search(pattern, string, re.MULTILINE)

    def _rrd_update(self, filename):
        if not os.path.exists(filename):
            self._create(filename)
        Rrd(filename).update(self._data)

    def show(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError


class UptimeMonitor(Monitor):
    def __init__(self):
        self._data = ()
        try:
            with open("/proc/uptime") as f:
                self._cmd = f.read()
        except:
            self._cmd = None

    def _parse(self):
        if self._cmd == None:
            self._data = 0, 0
        else:
            m = self._search("^([\d]+)\.\d+ ([\d]+)\.", self._cmd)
            self._data = tuple(map(int, m.group(1, 2)))

    def show(self):
        self._parse()

        print "Uptime:"
        print "    Uptime seconds :", self._data[0]
        print "    Idle seconds   :", self._data[1]
        print

    def _create(self, filename):
        rrd = Rrd(filename)
        rrd.add_counter('uptime_secs')
        rrd.add_counter('idle')
	rrd.create()

    def update(self, path):
        self._parse()
        self._rrd_update(path + '/uptime.rrd')
        

class LoadMonitor(Monitor):
    def __init__(self):
        self._data = ()
        try:
            with open("/proc/loadavg") as f:
                self._cmd = f.read()
        except:
            self._cmd = None

    def _parse(self):
        if self._cmd == None:
            self._data = 0, 0, 0
        else:
            m = self._search("^([\d.]+) ([\d.]+) ([\d.]+) ", self._cmd)
            self._data = tuple(map(float, m.group(1, 2, 3)))

    def show(self):
        self._parse()
        print "CPU load:"
        print "    1m  average :", self._data[0]
        print "    5m  average :", self._data[1]
        print "    15m average :", self._data[2]
        print

    def _create(self, filename):
        rrd = Rrd(filename)
        for i in [ 'load_1', 'load_5', 'load_15' ]:
            rrd.add_gauge(i)
	rrd.create()

    def update(self, path):
        self._parse()
        self._rrd_update(path + '/load.rrd')
        

class StatMonitor(Monitor):
    def __init__(self):
        self._data = ()
        try:
            with open("/proc/stat") as f:
                self._cmd = f.readline()
        except:
            self._cmd = None

    def _parse(self):
        if self._cmd == None:
            self._data = 0, 0, 0, 0, 0, 0, 0
        else:
            m = self._search('cpu\s+(\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+)',
                             self._cmd)
            self._data = tuple(map(int, m.group(1, 2, 3, 4, 5, 6, 7)))

    def show(self):
	self._parse()
        print 'CPU counters:'
        print '    User    :', self._data[0]
        print '    Nice    :', self._data[1]
        print '    System  :', self._data[2]
        print '    Idle    :', self._data[3]
        print '    IOwait  :', self._data[4]
        print '    IRQ     :', self._data[5]
        print '    Softirq :', self._data[6]
        print

    def _create(self, filename):
        rrd = Rrd(filename)
        for i in [ 'stat_user', 'stat_nice', 'stat_system', 'stat_idle',
                   'stat_iowait', 'stat_irq', 'stat_softirq' ]:
            rrd.add_counter(i)
	rrd.create()

    def update(self, path):
	self._parse()
        self._rrd_update(path + '/stat.rrd')
        

class MemMonitor(Monitor):
    def __init__(self):
        self._data = ()
        try:
            with open('/proc/meminfo') as f:
                self._cmd = f.read()
        except:
            self._cmd = None

    def _parse(self):
        t = ()
        for parm in [ 'MemTotal', 'MemFree', 'Buffers', 'Cached', 'Active',
                      'Inactive', 'SwapTotal', 'SwapFree' ]:
            if self._cmd == None:
                data = 0
            else:
                m = self._search('^' + parm + ':.* (\d+) ', self._cmd)
                data = int(m.group(1))
            t = t + (data,)
        self._data = t

    def show(self):
	self._parse()
        print 'Memory data:'
        print '    MemTotal  :', self._data[0]
        print '    MemFree   :', self._data[1]
        print '    Buffers   :', self._data[2]
        print '    Cached    :', self._data[3]
        print '    Active    :', self._data[4]
        print '    Inactive  :', self._data[5]
        print '    SwapTotal :', self._data[6]
        print '    SwapFree  :', self._data[7]
        print

    def _create(self, filename):
        rrd = Rrd(filename)
        for i in [ 'mem_total', 'mem_free', 'mem_buffers', 'mem_cached',
                   'mem_active', 'mem_inactive', 'swap_total', 'swap_free' ]:
            rrd.add_gauge(i)
	rrd.create()

    def update(self, path):
	self._parse()
        self._rrd_update(path + '/memory.rrd')


class VolMonitor(Monitor):
    def __init__(self, volumes, max_vols):
        self._volumes = volumes
        self._max_vols = max_vols
        self._cmd = self._run_command('df -m')
        self._data = ()

    def _parse(self):
        temp = [ 0 ] * (2 * self._max_vols)
        i = 0
        for v in self._volumes:
            m = self._search('^' + v[0] + '\s+(\d+)\s+(\d+)', self._cmd)
            temp[i], temp[i + 1] = tuple(map(int, m.group(1, 2)))
            i = i + 2
        self._data = temp

    def show(self):
        self._parse()
        print "Volume data:"
        i = 0
        for v in self._volumes:
            print "    %s [%s]:" % v
            print "        Total   : %d" % (self._data[i])
            print "        Used    : %d" % (self._data[i + 1])
            print "        Percent : %4.1f%%" % (100.0 * self._data[i + 1]
                                                 / self._data[i])
            print
            i = i + 2

    def _create(self, filename):
        rrd = Rrd(filename)
        for i in range(self._max_vols):
            vol = "vol%d_" % (i)
            rrd.add_gauge(vol + 'total')
            rrd.add_gauge(vol + 'used')
	rrd.create()

    def update(self, path):
	self._parse()
        self._rrd_update(path + '/volumes.rrd')


class HDMonitor(Monitor):
    def __init__(self, hds, max_hds):
        self._hds = hds
        self._max_hds = max_hds
        self._cmd = { }
        self._data = ()

        for hd in hds:
            self._cmd[hd] = self._run_command('smartctl -d ata -A /dev/' + hd)

    def _parse(self):
        temp = [ 0 ] * (3 * self._max_hds)
        i = 0
        for hd in self._hds:
            if self._cmd[hd] == None:
                data = [ 0, 0, 0 ] 
            else:
                data = [ ]
                for parm in [ 'Temperature_Celsius', 'Power_On_Hours',
                              'Start_Stop_Count' ]:
                   m = self._search(parm + ' .* (\d+)( \(.*\))?$', self._cmd[hd])
                   data.append(int(m.group(1)))
            temp[i], temp[i + 1], temp[i + 2] = data
            i = i + 3

        self._data = tuple(temp)

    def show(self):
        self._parse()
        print 'Hard disk data:'
        i = 0
        for hd in self._hds:
            print "    %s:" % (hd)
            print '        Temperature      :', self._data[i], '°C' 
            print '        Power-on hours   :', self._data[i + 1]
            print '        Start/stop count :', self._data[i + 2]
            print
            i = i + 3

    def _create(self, filename):
        rrd = Rrd(filename)
        for i in range(self._max_hds):
            hd = "hd%d_" % i
            rrd.add_gauge(hd + 'temp')
            rrd.add_gauge(hd + 'hours')
            rrd.add_gauge(hd + 'starts')
	rrd.create()

    def update(self, path):
	self._parse()
        self._rrd_update(path + '/hds.rrd')


class IOMonitor(Monitor):
    def __init__(self, hds, max_hds):
        self._hds = hds
        self._max_hds = max_hds
        self._cmd = { }
        self._data = ()

        for hd in hds:
            try:
                with open('/sys/block/' + hd + '/stat') as f:
                    self._cmd[hd] = map(int, f.readline().split())
            except:
                self._cmd[hd] = [ 0 ] * 11

    def _parse(self):
        temp = [ 0 ] * (4 * self._max_hds)
        i = 0
        for hd in self._hds:
            line = self._cmd[hd]
            temp[i] = line[2]
            temp[i + 1] = line[2]
            temp[i + 2] = line[6]
            temp[i + 3] = line[7]
            i = i + 4

        self._data = temp

    def show(self):
        self._parse()
        print 'Hard disk I/O data:'
        i = 0
        for hd in self._hds:
            print "    %s:" % (hd)
            print '        Sectors read     :', self._data[i    ]
            print '        Read time        :', self._data[i + 1], 'ms'
            print '        Sectors written  :', self._data[i + 2]
            print '        Write time       :', self._data[i + 3], 'ms'
            print
            i = i + 4

    def _create(self, filename):
        rrd = Rrd(filename)
        for i in range(self._max_hds):
            hd = "hd%d_" % i
            rrd.add_counter(hd + 'reads')
            rrd.add_counter(hd + 'readtime')
            rrd.add_counter(hd + 'writes')
            rrd.add_counter(hd + 'writetime')
	rrd.create()

    def update(self, path):
	self._parse()
        self._rrd_update(path + '/hdio.rrd')


class NetMonitor(Monitor):
    def __init__(self, ifaces, max_lan):
        self._ifaces = ifaces
        self._max_lan = max_lan
        self._cmd = { }
        self._data = ()

        for i in ifaces:
            self._cmd[i] = self._run_command("ifconfig " + i)

    def _parse(self):
        temp = [ 0 ] * (2 * self._max_lan)
        i = 0
        for iface in self._ifaces:
            m = self._search("RX bytes:(\d+) .*TX bytes:(\d+)", self._cmd[iface])
            temp[i], temp[i + 1] = tuple(map(int, m.group(1, 2)))
            i += 2
        self._data = temp

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

    def _create(self, filename):
        rrd = Rrd(filename)
        for i in range(self._max_lan):
            lan = "eth%d_" % (i)
            rrd.add_counter(lan + "rx")
            rrd.add_counter(lan + "tx")
	rrd.create()

    def update(self, path):
        self._parse()
        self._rrd_update(path + '/network.rrd')
