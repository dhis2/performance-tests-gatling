## Toxiproxy

### Setup

* DHIS2 is connected to the DB and minio via the proxy
* prometheus and the user creation via mc is done via minio without the proxy

### Chaos

https://github.com/Shopify/toxiproxy#toxics

List/inspect proxies

```sh
docker compose exec proxy /toxiproxy-cli list
docker compose exec proxy /toxiproxy-cli inspect dhis2_core_web_1
```

Add a toxic to a proxy

```sh
docker compose exec proxy /toxiproxy-cli toxic add -t latency -a latency=100 -a jitter=50 dhis2_core_web_1
```

Disable a proxy

```sh
docker compose exec proxy /toxiproxy-cli toggle dhis2_core_web_1
```

