from twisted.internet.base import ThreadedResolver as _ThreadedResolverImpl

from twisted.web.server import Site, NOT_DONE_YET
from twisted.web.resource import Resource
from twisted.names import dns, client, root, cache, resolve, hosts, common as namesCommon
from twisted.internet import reactor

import httpresolver
import logging
logging.basicConfig(level=logging.INFO)
DNSLogger = logging.getLogger('DNSHTTPServer')

typeToMethod = namesCommon.typeToMethod

class BadRequest(Resource):
    def __init__(self, message=''):
        Resource.__init__(self)
        self.message = message
    def render_GET(self, request):
        request.setResponseCode(400)
        return "<html><head><title>Bad Request</title></head><body><center><h1>Bad Request</h1></center></body></html>"

class JustAPath(Resource):
    def render_GET(self, request):
        return BadRequest(request)

class ResolveHere(Resource):
    def __init__(self,queryClass,typeKey,short=False):
        Resource.__init__(self)
        self.queryClass = queryClass
        self.typeKey = typeKey
        self.short = short
    def getChild(self,path,request):
        return doLookUp(self.queryClass,self.typeKey,path,self.short)

    def render_GET(self,request):
        return BadRequest(request)

class doLookUp(Resource):
    def __init__(self,queryClass,typeKey,query,short=False):
        Resource.__init__(self)
        self.queryClass = queryClass
        self.whatType= typeKey
        self.whatQuery = query
        self.short = short

    def render_GET(self,request):
        DNSLogger.info("REQUEST: %s" % (request))
        self.handleHTTPRequest(request)
        return NOT_DONE_YET

    def handleHTTPRequest(self,request):
        d=theResolver.typeToMethod[self.whatType](self.whatQuery)
        if self.short:
            d.addCallback(httpresolver.returnAnswerHTTP,request)
        else:
            d.addCallback(httpresolver.returnResultsHTTP,request)
        d.addErrback(httpresolver.returnErrorHTTP,request)
        request.notifyFinish().addErrback(httpresolver.cancelHTTPRequest, d, request)

#theResolver = client.Resolver('/etc/resolv.conf')
theResolver=None
if __name__ == "__main__":
    resolvers=[]
    cacheResolver = cache.CacheResolver(verbose=True)
    resolvers.append(cacheResolver)
    ##clientResolver = client.Resolver(servers=[('127.0.0.1',1023)])
    clientResolver = client.Resolver(servers=[('8.8.8.8',53),('8.8.4.4',53)])
    #hostResolver = hosts.Resolver(file='named.root.txt')
    #rootResolver = root.bootstrap(hostResolver)
    #resolvers.append(rootResolver)
    ##resolvers.append(hostResolver)
    resolvers.append(clientResolver)
    theResolver = resolve.ResolverChain(resolvers)

    root = Resource()
    PROXY = JustAPath()
    root.putChild('PROXY',PROXY)
    IN_PROXY = JustAPath()
    PROXY.putChild('IN',IN_PROXY)
    SHORT = JustAPath()
    root.putChild('SHORT',SHORT)
    IN_SHORT = JustAPath()
    SHORT.putChild('IN',IN_SHORT)
    # ANY = Nameservice()
    for (k, v) in dns.QUERY_TYPES.items() + dns.EXT_QUERIES.items():
        # print "%s\n" % v
        try:
            m = typeToMethod[k]
        except KeyError:
            pass
        else:
            IN_PROXY.putChild(v,ResolveHere(dns.IN,k,short=False))
            IN_SHORT.putChild(v,ResolveHere(dns.IN,k,short=True))
    factory = Site(root)
    reactor.listenTCP(8882, factory)
    reactor.run()
