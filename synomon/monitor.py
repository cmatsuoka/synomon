import subprocess
import re

class Monitor:
    def _run_command(self, cmd):
        try:
            return subprocess.check_output(cmd.split())
        except:
            return None

    def _search(self, pattern, string):
        return re.search(pattern, string, re.MULTILINE)

    def parse(self):
        raise NotImplementedError

    def show(self):
        raise NotImplementedError

    def get_data(self):
        raise NotImplementedError

class CPUMonitor(Monitor):
    def __init__(self):
        self._data = ()
        try:
            with open("/proc/loadavg") as f:
                self._cmd = f.read()
        except:
            self._cmd = None

    def parse(self):
        if self._cmd == None:
            self._data = 0, 0, 0
        else:
            m = self._search("^([\d.]+) ([\d.]+) ([\d.]+) ", self._cmd)
            self._data = tuple(map(float, m.group(1, 2, 3)))

    def show(self):
        print "CPU load:"
        print "    1m  average :", self._data[0]
        print "    5m  average :", self._data[1]
        print "    15m average :", self._data[2]
        print

    def get_data(self):
        return self._data

class MemMonitor(Monitor):
    def __init__(self):
        self._data = { }
        try:
            with open("/proc/meminfo") as f:
                self._cmd = f.read()
        except:
            self._cmd = None

    def parse(self, parm):
        if self._cmd == None:
            self._data[parm] = 0
        else:
            m = self._search("^" + parm + ":.* (\d+) ", self._cmd)
            self._data[parm] = int(m.group(1))

    def show(self):
        print "Memory data:"
        for i in sorted(self._data.keys()):
            print "    %-10.10s: %d kB" % (i, self._data[i])
        print

    def get_data(self):
        t = ()
        for i in [ "MemTotal", "MemFree", "Buffers", "Cached", "Active",
                   "Inactive", "SwapTotal", "SwapFree" ]:
            t = t + (self._data[i],)
        return t

class VolMonitor(Monitor):
    def __init__(self):
        self._cmd = self._run_command("df -m")
        self._data = { }

    def parse(self, dev):
        m = self._search("^" + dev + "\s+(\d+)\s+(\d+)", self._cmd)
        self._data[dev] = map(int, m.group(1, 2))

    def show(self):
        print "Volume data:"
        for i in sorted(self._data.keys()):
            print "    %s:" % (i)
            print "        Total   : %d" % (self._data[i][0])
            print "        Used    : %d" % (self._data[i][1])
            print "        Percent : %4.1f%%" % (100.0 * self._data[i][1]
                                                 / self._data[i][0])
            print

    def get_data(self, dev):
        return tuple(self._data[dev])

class HDMonitor(Monitor):
    def __init__(self, hdlist):
        self._cmd = { }
        self._data = { }

        for hd in hdlist:
            self._cmd[hd] = self._run_command("smartctl -d ata -A /dev/" + hd)
            self._data[hd] = { }

    def parse(self, hd, parm):
        if self._cmd[hd] == None:
            self._data[hd][parm] = 0
        else:
            m = self._search(parm + " .* (\d+)( \(.*\))?$", self._cmd[hd])
            self._data[hd][parm] = int(m.group(1))

    def show(self):
        print "Hard disk data:"
        for i in sorted(self._data.keys()):
            print "    %s:" % (i)
            for j in self._data[i].keys():
                print "        %-20.20s: %d" % (j, self._data[i][j])
            print

    def get_data(self, hd):
        return (self._data[hd]['Temperature_Celsius'],
                self._data[hd]['Power_On_Hours'],
                self._data[hd]['Start_Stop_Count'])

class IOMonitor(Monitor):
    def __init__(self, hdlist):
        self._line = { }
        self._data = { }

        for dev in hdlist:
            try:
                with open("/sys/block/" + dev + "/stat") as f:
                    self._line[dev] = map(int, f.readline().split())
            except:
                self._line[dev] = [ 0 ] * 11


    def parse(self, dev):
        line = self._line[dev]
        self._data[dev] = line[2], line[3], line[6], line[7]

    def show(self):
        print "IO data:"
        for i in sorted(self._data.keys()):
            print "    %s:" % (i)
            print "        Sector reads  : %d" % (self._data[i][0])
            print "        Read time     : %d ms" % (self._data[i][1])
            print "        Sector writes : %d" % (self._data[i][2])
            print "        Write time    : %d ms" % (self._data[i][3])
            print
        pass

    def get_data(self, dev):
        return tuple(self._data[dev])

class NetMonitor(Monitor):
    def __init__(self, iflist):
        self._cmd = { }
        self._data = { }

        for i in iflist:
            self._cmd[i] = self._run_command("ifconfig " + i)

    def parse(self, iface):
        m = self._search("RX bytes:(\d+) .*TX bytes:(\d+)", self._cmd[iface])
        self._data[iface] = map(int, m.group(1, 2))

    def show(self):
        print "Network interface data:"
        for i in sorted(self._data.keys()):
            print "    %s:" % (i)
            print "        Rx bytes : %d" % (self._data[i][0])
            print "        Tx bytes : %d" % (self._data[i][1])
            print

    def get_data(self, iface):
        return tuple(self._data[iface])

