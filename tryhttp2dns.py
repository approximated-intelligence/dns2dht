from twisted.names import dns, common as namesCommon

from twisted.internet import reactor
import sys

import httpresolver

def gotAddress(a):
    print 'Addresses: ', ', '.join(map(str, a))
    reactor.stop()

def gotError(f):
    print 'gotError'
    f.printTraceback()

    from twisted.internet import reactor
    reactor.stop()

r=httpresolver.HTTPResolver('127.0.0.1',8882)
#r.getHostByName("www.heise.de").addCallback(gotName)
try:
  name=sys.argv[1]
except:
  name='www.heise.de'
finally:
  r.lookupAddress(name).addCallback(gotAddress).addErrback(gotError)

reactor.run()
