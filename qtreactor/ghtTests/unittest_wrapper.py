from __future__ import print_function
__author__ = 'ght'

import qtreactor.pyqt4reactor
#qtreactor.pyqt4reactor.install()

from twisted.application import reactors
reactors.installReactor('pyqt4')

#from ghtTests.texboxtest import buildgui

#form = buildgui()

import sys
#log.startLogging(sys.stdout)

trialpath = '/usr/local/bin/trial'
trial = open(trialpath,'r').read()

import contextlib
@contextlib.contextmanager
def redirect_argv(num):
    sys._argv = sys.argv[:]
    sys.argv[:] = num
    yield
    sys.argv[:] = sys._argv


#sys.stdout = open('/tmp/unitspew.txt','w')
with redirect_argv([trialpath,
                    'twisted.test.test_ftp',
                    'twisted.test.test_internet']):
    exec (trial)
