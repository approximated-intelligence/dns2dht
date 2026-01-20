from twisted.python import failure
from twisted.names import dns

import socket
import simplejson

from common import ALL_TYPES

import logging
logging.basicConfig(level=logging.INFO)
PickleLogger = logging.getLogger('Pickle')
UnpickleLogger = logging.getLogger('Unpickle')

def unpickleRR(dct):
    if '__type__' in dct:
        objType=dct['__type__'];
        if (objType=='RRHeader'):
            UnpickleLogger.debug('dct: %s' % str(dct))
            rr = dns.RRHeader(dct['name'],dns.REV_TYPES[dct['type']],dns.REV_CLASSES[dct['cls']],dct['ttl'],dct['payload'],dct['auth'])
            return rr
        elif (objType=='Name'):
            return 'objType:Name - should not happen' #dns.Name(dct['name'])
        elif (objType=='Record_A'):
            return dns.Record_A(dct['address'],dct['ttl'])
        elif (objType=='Record_AAAA'):
            return dns.Record_AAAA(dct['address'],dct['ttl'])
        elif (objType=='Record_CNAME'):
            return dns.Record_CNAME(dct['name'],dct['ttl'])
        elif (objType=='Record_DNAME'):
            return dns.Record_DNAME(dct['name'],dct['ttl'])
        elif (objType=='Record_NS'):
            return dns.Record_NS(dct['name'],dct['ttl'])
        elif (objType=='Record_PTR'):
            return dns.Record_PTR(dct['name'],dct['ttl'])
        elif (objType=='Record_SOA'):
            return dns.Record_SOA(dct['mname'], dct['rname'], dct['serial'], dct['refresh'], dct['retry'], dct['expire'], dct['minimum'], dct['ttl'])
        elif (objType=='Record_TXT'):            
            return dns.Record_TXT(dct['data'],ttl=dct['ttl'])
        elif (objType=='Failure'):
            return failure.Failure(dct['value'],dct['type'])
        else:
            return {objType:'unimplemented'}

class RRPickleClass(simplejson.JSONEncoder):
    def default(self,obj):
        #PickleLogger.debug('TYPE: %s' % type(obj).__name__)
        #print "called for %s(%s)" % (type(obj).__name__,self.classname(obj)) #,obj)
        if type(obj).__name__=='instance':
            cls=obj.__class__.__name__
            if (cls==dns.RRHeader.__name__):
                #return {'name':obj.name.name,'type':obj.type,'__type__':obj.cls,'ttl':obj.ttl,'auth':obj.auth}
                return {'__type__':cls, 'name':obj.name, 'type':ALL_TYPES[obj.type], 'cls':dns.QUERY_CLASSES[obj.cls], 'ttl':obj.ttl, 'payload':obj.payload, 'auth':obj.auth} #, 'rdlength':obj.rdlength}
            elif (cls==dns.Name.__name__):
                return obj.name #{'__type__':cls, 'name':obj.name}
            elif (cls==dns.Record_A.__name__):
                return {'__type__':cls, 'address':socket.inet_ntoa(obj.address), 'ttl':obj.ttl}
            elif (cls==dns.Record_AAAA.__name__):
                return {'__type__':cls, 'address':socket.inet_ntop(socket.AF_INET6,obj.address), 'ttl':obj.ttl}
            elif (cls==dns.Record_CNAME.__name__):
                return {'__type__':cls, 'name':obj.name, 'ttl':obj.ttl}
            elif (cls==dns.Record_DNAME.__name__):
                return {'__type__':cls, 'name':obj.name, 'ttl':obj.ttl}
            elif (cls==dns.Record_NS.__name__):
                return {'__type__':cls, 'name':obj.name, 'ttl':obj.ttl}
            elif (cls==dns.Record_PTR.__name__):
                return {'__type__':cls, 'name':obj.name, 'ttl':obj.ttl}
            elif (cls==dns.Record_SOA.__name__):
                return {'__type__':cls, 'mname':obj.mname, 'rname':obj.rname, 'serial':obj.serial, 'refresh':obj.refresh, 'retry':obj.retry, 'expire':obj.expire, 'minimum':obj.minimum, 'ttl':obj.ttl}
            elif (cls==dns.Record_TXT.__name__):
                return {'__type__':cls, 'data':obj.data[0], 'ttl':obj.ttl}
            elif (cls==failure.Failure.__name__):
                return {'__type__':cls, 'value':obj.value, 'type':obj.type}
            else:
                return {'__type__':cls, 'notimplemented':True}
        else:
            return simplejson.JSONEncoder.default(self, obj)

def dumpRR(obj):
    return simplejson.dumps(obj,cls=RRPickleClass,separators=(',', ':'),)
def loadRR(obj):
    return simplejson.loads(obj,object_hook=unpickleRR)
