from twisted.names import dns, client, cache, server, common as namesCommon

from twisted.internet import reactor
import sys

#resolver = client.Resolver(servers=[('8.8.8.8',53),('8.8.4.4',53)])
#cacher = cache.CacheResolver(verbose=True)
#f = server.DNSServerFactory(caches=[cacher],clients=[resolver], verbose=True)
resolver = client.Resolver(servers=[('127.0.0.1',1053)])
f = server.DNSServerFactory(caches=[],clients=[resolver], verbose=True)
p = dns.DNSDatagramProtocol(f)
f.noisy = p.noisy = True

reactor.listenUDP(53, p)
reactor.listenTCP(53, f)
reactor.run()

