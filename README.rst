
This is a work-in-progress monitor script I'm using on my Synology
DiskStation DS212j NAS. It gathers data from different sources and
stores/presents them using Tobias Oetiker's RRDtool_.

Quick start
-----------

Things you need in order to run the monitor:

 * Bootstrap: you'll need a number of third-party packages available on
   a bootstrapped DiskStation. Check this bootstrapping-guide_ to learn
   how to do it.

 * Python: it can be installed from Package Center

 * RRDtool ::
    > ipkg install rrdtool

 * PyRRD_ ::
    > curl -k https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python
    > pip install PyRRD


Configuration
-------------


Usage
-----



.. _bootstrapping-guide: http://zubinraj.wordpress.com/2012/07/19/bootstrapping-synology-diskstation-unleash-the-power/
.. _RRDtool: http://oss.oetiker.ch/rrdtool/
.. _PyRRD: http://pypi.python.org/pypi/PyRRD/
