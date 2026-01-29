from twisted.names import dns, cache, client, resolve, common as namesCommon

from twisted.names.error import DNSFormatError, DNSServerError, DNSNameError
from twisted.names.error import DNSNotImplementedError, DNSQueryRefusedError
from twisted.names.error import DNSUnknownError, DNSQueryTimeoutError

import pickleRR
from common import ALL_TYPES

import hashlib
from base64 import b64encode

from twisted.internet import defer, reactor

import logging
logging.basicConfig(level=logging.DEBUG)
DHTLogger = logging.getLogger('DHTlib')

class DHTResolver(namesCommon.ResolverBase):
    def __init__(self, node, resolver=None):
        self.node = node
        self.typeToMethod = {}
        self.resolver=resolver
        for (k, v) in namesCommon.typeToMethod.items():
            self.typeToMethod[k] = getattr(self, v)

    def _lookup(self, name, queryClass, queryType, timeout):
        uri=('dns://%s/%s/%s' % (dns.QUERY_CLASSES[queryClass],ALL_TYPES[queryType],name))
        h=hashlib.sha1()
        h.update(uri)
        key=h.digest()

        # outer Deferred to be called back with result RR
        outerDf = defer.Deferred()

        def dhtResult(result):
            DHTLogger.debug('GOT %s for REQUEST %s [%s]' % (result,uri,b64encode(key)))
            if type(result) == dict:
                # We have found the value;
                DHTLogger.info('FOUND %s for REQUEST %s' % (result[key],uri))
                RR=pickleRR.loadRR(result[key])
                outerDf.callback(RR)
            else:
                # The value wasn't found, but a list of contacts was returned
                # Now, see if we have the value (it might seem wasteful to search on the network
                # first, but it ensures that all values are properly propagated through the
                # network
                # Ok, value does not exist in DHT at all
                # fetch it from DNS
                DHTLogger.info('FETCHING %s from DNS' % (uri))
                def dnsAnswer(DNSRR):
                    DHTLogger.debug('GOT %s from DNS for %s' % (DNSRR,name))
                    value=pickleRR.dumpRR(DNSRR)
                    DHTLogger.info('STORING %s for key %s [%s] from DNS' % (value,uri,b64encode(key)))
                    self.node.iterativeStore(key,value)
                    outerDf.callback(DNSRR)
                    
                def dnsError(f):
                    error=f.trap(DNSServerError,DNSNameError,DNSQueryRefusedError,DNSQueryTimeoutError)
                    #error=f.trap(DNSFormatError,DNSNotImplementedError,DNSUnknownError)
                    message=f.getErrorMessage()
                    DHTLogger.critical("DNS FAILURE: %s(%s) for %s" % (error.__name__,message,uri))
                    outerDf.errback(f)
                d=self.resolver.typeToMethod[queryType](name)
                d.addCallback(dnsAnswer).addErrback(dnsError)
                
        def dhtError(f):
            message=f.getErrorMessage()
            DHTLogger.critical("DHT FAILURE: %s for %s [%s]" % (message,uri,key))
            outerDf.errback(f)  # call the error callback of the outer Deferred
            
        DHTLogger.info('REQUESTING %s [%s]' % (uri,b64encode(key)))
        self.node.iterativeFindValue(key).addCallback(dhtResult).addErrback(dhtError)
        return outerDf
