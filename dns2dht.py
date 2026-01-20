from twisted.names import dns, cache, client, server, common as namesCommon

from twisted.internet import reactor
import sys

import entangled
import dhtresolver
from entangled.kademlia.node import Node
from entangled.kademlia.datastore import SQLiteDataStore

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print 'Usage:\n%s UDP_PORT  [KNOWN_NODE_IP  KNOWN_NODE_PORT]' % sys.argv[0]
        print 'or:\n%s UDP_PORT  [FILE_WITH_KNOWN_NODES]' % sys.argv[0]
        print '\nIf a file is specified, it should containg one IP address and UDP port\nper line, seperated by a space.'
        sys.exit(1)
    try:
        usePort = int(sys.argv[1])
    except ValueError:
        print '\nUDP_PORT must be an integer value.\n'
        print 'Usage:\n%s UDP_PORT  [KNOWN_NODE_IP  KNOWN_NODE_PORT]' % sys.argv[0]
        print 'or:\n%s UDP_PORT  [FILE_WITH_KNOWN_NODES]' % sys.argv[0]
        print '\nIf a file is specified, it should contain one IP address and UDP port\nper line, seperated by a space.'
        sys.exit(1)

    if len(sys.argv) == 4:
        knownNodes = [(sys.argv[2], int(sys.argv[3]))]
    elif len(sys.argv) == 3:
        knownNodes = []
        f = open(sys.argv[2], 'r')
        lines = f.readlines()
        f.close()
        for line in lines:
            ipAddress, udpPort = line.split()
            knownNodes.append((ipAddress, int(udpPort)))
    else:
        knownNodes = None

    dataStore = SQLiteDataStore(dbFile = '/tmp/dbFile%s.db' % usePort)
    aNode = Node ( udpPort=usePort, dataStore=dataStore )
    aNode.joinNetwork(knownNodes)

    #resolvers=[]
    #cacheResolver = cache.CacheResolver(verbose=True)
    #resolvers.append(cacheResolver)
    ##clientResolver = client.Resolver(servers=[('127.0.0.1',1023)])
    clientResolver = client.Resolver(servers=[('8.8.8.8',53),('8.8.4.4',53)])
    ##hostResolver = hosts.Resolver(file='named.root.txt')
    ##rootResolver = root.bootstrap(hostResolver)
    ##resolvers.append(rootResolver)
    ###resolvers.append(hostResolver)
    #resolvers.append(clientResolver)
    #theResolver = resolve.ResolverChain(resolvers)
    theResolver=clientResolver
    resolver = dhtresolver.DHTResolver( aNode, resolver=theResolver )
    #cacher = cache.CacheResolver(verbose=True)
    #f = server.DNSServerFactory(caches=[cacher],clients=[resolver], verbose=True)
    f = server.DNSServerFactory(caches=[],clients=[resolver], verbose=True)
    p = dns.DNSDatagramProtocol(f)
    f.noisy = p.noisy = True

    reactor.listenUDP(1053, p)
    reactor.listenTCP(1053, f)
    reactor.run()

