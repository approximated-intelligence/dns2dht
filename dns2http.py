from twisted.names import dns, cache, server, common as namesCommon

from twisted.internet import reactor
import sys

import httpresolver

resolver = httpresolver.HTTPResolver(server='127.0.0.1', port=8882, path='PROXY')
cacher = cache.CacheResolver(verbose=True)
f = server.DNSServerFactory(caches=[cacher],clients=[resolver], verbose=True)
p = dns.DNSDatagramProtocol(f)
f.noisy = p.noisy = True

reactor.listenUDP(1053, p)
reactor.listenTCP(1053, f)
reactor.run()

