# DHT DNS Resolver Prototype Suite (2009)

> **Historical context:** This code was publicly demonstrated at **26C3, December 2009**:  
> [https://media.ccc.de/v/26c3-3594-de-internetsperren](https://media.ccc.de/v/26c3-3594-de-internetsperren)  
> It predates DNS-over-HTTPS: [https://en.wikipedia.org/wiki/DNS_over_HTTPS](https://en.wikipedia.org/wiki/DNS_over_HTTPS)  
> Other projects for decentralized DNS over a DHT include the peer-to-peer DNS over DHT by Peter Sunde from November 2010:  
> [https://www.golem.de/1012/79791.html](https://www.golem.de/1012/79791.html)  
> [https://p2pdns.baywords.com/2010/11/30/hello-world/](https://p2pdns.baywords.com/2010/11/30/hello-world/)   
> [http://twitter.com/brokep/status/8768724777574401](http://twitter.com/brokep/status/8768724777574401)

---

## Overview

A proof-of-concept **decentralized DNS/HTTP resolution system** using a **Kademlia-based DHT** (`entangled`) to store DNS records. Queries resolve peer-to-peer first, with fallback to conventional DNS if missing. Focus is on **resilient, censorship-resistant name resolution**.

---

## Architecture

- **DHT Node:** Persistent `SQLiteDataStore`. Nodes bootstrap via known peers or a file.  
- **Resolvers:**  
  - `DHTResolver`: Queries the DHT first, falling back to Twisted DNS.  
  - `HTTPResolver`: Fetches DNS records over HTTP from DHT-backed servers (`dns2http.py`), which can in turn query the DHT nodes.  
- **Serialization:** DNS records stored as JSON via `pickleRR.py`.  
- **Networking:** Fully asynchronous with Twisted; DNS and HTTP layers wrap the node.  
- **HTTPS note:** Enabling HTTPS for the HTTP DNS proxy requires only minor modifications: wrap the Twisted HTTP server in TLS (`reactor.listenSSL`) and provide a TLS context to clients (`twisted.internet.ssl.ClientContextFactory`).

---

## Files

- `dns2dht.py` — DHT node with Twisted DNS front-end (`DHTResolver`).  
- `dns2dns.py` — DNS proxy forwarding queries to another resolver.  
- `dns2http.py` — Exposes DHT-stored DNS records via HTTP, usable by `HTTPResolver`.  
- `http2dns.py` — HTTP server providing DNS query endpoints for clients.  
- `tryhttp2dns.py` — Client testing `http2dns.py`.  
- `dhtresolver.py` — Twisted resolver using the DHT, with DNS fallback.  
- `httpresolver.py` — Twisted resolver fetching DNS records over HTTP from `dns2http.py`.  
- `pickleRR.py` — Serializes/deserializes DNS records to/from JSON.  
- `common.py` — Shared DNS constants and type mappings.

---

## Usage

1. Launch each `dns2dht.py` instance on a unique UDP port.  
2. Provide known nodes via command-line or file.  
3. Nodes communicate using SHA1 hashes of `dns://<CLASS>/<TYPE>/<NAME>`.  
4. HTTP/DNS front-ends are optional.  
5. `dns2http.py` can expose DHT nodes via HTTP, and `http2dns.py` clients can query these servers.

**Bootstrap example:**

- Node 1: `python dns2dht.py 4001`  
- Node 2: `python dns2dht.py 4002 127.0.0.1 4001`  
- Node 3: `python dns2dht.py 4003 nodes.txt` (file contains other nodes’ IPs and ports)  
- Start HTTP front-end: `python dns2http.py`  
- Client queries via HTTP: `python http2dns.py`

---

## Notes

- Python 2-era code; Twisted APIs will require older versions.  
- Dependencies: Twisted, SQLite.  
- GUI components are excluded.  
- Serialization is JSON-like but specific to DNS RR objects.  
- Early demonstratio of peer-to-peer DNS over DHT
- Also demonstrates DNS over HTTP well before DoH.

---

## License

GPL (GNU General Public License Version 3 or later).
