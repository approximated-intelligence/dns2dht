from twisted.names import dns, common as namesCommon
from twisted.web import client
from twisted.web.error import Error as WebError

from twisted.names.error import DNSFormatError, DNSServerError, DNSNameError
from twisted.names.error import DNSNotImplementedError, DNSQueryRefusedError
from twisted.names.error import DNSUnknownError, DNSQueryTimeoutError

import pickleRR
from common import ALL_TYPES

import logging
logging.basicConfig(level=logging.DEBUG)
HTTPLogger = logging.getLogger('HTTPlib')


class HTTPResolver(namesCommon.ResolverBase):
    def __init__(self,server='127.0.0.1',port=8882,path='PROXY'):
        self.server=server
        self.port=port
        self.typeToMethod = {}
        self.path=path
        for (k, v) in namesCommon.typeToMethod.items():
            self.typeToMethod[k] = getattr(self, v)

    def gotResult(self,result,request):
        HTTPLogger.debug('GOT: %s for REQUEST: %s' % (result,request))
        RR=pickleRR.loadRR(result)
        HTTPLogger.debug('RR: %s' % ', '.join(map(str,RR)))
        return RR

    def gotFailure(self,failure,request):
        error=failure.trap(WebError)
        message=failure.getErrorMessage()
        #failure.printTraceback()
        HTTPLogger.critical("FAILURE: %s(%s) for REQUEST: %s" % (error.__name__,message,request))
        raise DNSServerError, message
    def _lookup(self, name, cls, type, timeout):
        page=('http://%s:%d/%s/%s/%s/%s' % (self.server,self.port,self.path,dns.QUERY_CLASSES[cls],ALL_TYPES[type],name))
        HTTPLogger.info('REQUESTING: %s' % page)
        return client.getPage(page).addCallback(self.gotResult,page).addErrback(self.gotFailure,page)


def returnAnswerHTTP(result, request):
    (answers,auth,additional) = result
    HTTPLogger.info("RESULTS: %s for REQUEST:%s" % (','.join([str(x.payload) for x in answers]),request))
    pickled='['+','.join([pickleRR.dumpRR(x.payload) for x in answers]) + ']'
    HTTPLogger.debug("simplejson: %s" % (pickled))
    request.setHeader("Content-Type","application/json")
    request.write("%s" % (pickled))
    request.finish()

def returnResultsHTTP(result, request):
    (answers,auth,additional) = result
    HTTPLogger.info("RESULTS: %s for REQUEST:%s" % (','.join([str(x.payload) for x in answers]),request))
    pickled=pickleRR.dumpRR(result)
    HTTPLogger.debug("simplejson: %s" % (pickled))
    request.setHeader("Content-Type","application/json")
    request.write("%s" % (pickled))
    request.finish()

def returnErrorHTTP(failure, request):
    error=failure.trap(DNSServerError,DNSNameError,DNSQueryRefusedError,DNSQueryTimeoutError)
    # error=failure.trap(DNSFormatError, DNSServerError, DNSNameError,
    #                    DNSNotImplementedError, DNSQueryRefusedError,
    #                    DNSUnknownError)
    message=failure.getErrorMessage()
    HTTPLogger.critical("FAILURE: %s(%s) for REQUEST: %s" % (error.__name__,message,request))
    if (error==DNSNameError):
        request.setResponseCode(404)
    elif (error==DNSQueryRefusedError):
        request.setResponseCode(403)
    elif (error==DNSQueryTimeoutError):
        request.setResponseCode(408)
    elif (error==DNSServerError):
        request.setResponseCode(502)
    else:
        request.setResponseCode(500)
    request.setHeader("Content-Type","application/json")
    response='[[{"__type__":"error", "class":"%s"}]]' % (error.__name__)
    HTTPLogger.info("FAILURE RESPONSE: %s" % response)
    request.write(response)
    request.finish()

def cancelHTTPRequest(failure,defered,request):
    HTTPLogger.debug("CANCELED: %s" % (request))
    #defered.cancel()
    #err(failure,"Canceled Request")
