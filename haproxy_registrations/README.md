# corpusops.roles/haproxy_registrations ansible role
## Documentation
Managment of haproxy objects

- see [filter plugin](../ansible_plugins/filter_plugins/copsf_haproxy.py)
- see [haproxy_server role vars](../services_proxy_haproxy_vars)
- see [haproxy_server role](../services_proxy_haproxy)
- see [defaults](./defaults/main.yml)
- see [template](./templates/cfg.cfg)
- see [tests](./test.yml)

### Configure haproxy objects
- tasks/main.yml
    ```yaml
    - include_role: {name: corpusops.roles/haproxy_registrations}
      vars:
        _corpusops_haproxy_registrations:
          file: /etc/haproxy/cfg.d/registrations.cfg
          frontends: {list of raw frontends}
          backends: {list or raw backends}
          listeners: {list of raw listeners}
          dispatchers: {list of raw dispatchers}
          registrations: {specific list of registrations (avoid corpusops_haproxy_registrations_registrations_*)}
    ```

## Idea
- We provide a facility to auto configure HTTP/HTTPS/REDIS/TCP backends
  via the informations that we can discover in the pillar.
- We want in an future iteration to add a discovery mecanism, maybe via
  the mine or a discovery service like ETCD, zookeeper or consul.
- The subkey for configuring proxies is the
  `corpusops_haproxy_registrations.registrations` dict

## How to use
```yaml
corpusops_haproxy_registrations_registrations_<arbitrar id>:
    - ip: <local_ip of backend>
      frontends:
        <frontend_port>:
            to_port: <dest_port>, # optional, default to <frontend_port>
            mode: <http/https/tcp/tcps/redis>
            # those opts act on frontend tied's backend
            # ssl_terminated: true/false
            # ssl_check: 'ssl verify none'
            # inter_check: 'inter 1s'
            # raw_srv: 'weight 100'
      hosts: [<hosts_to_proxy_from>]     # only useful on http(s) mode
      regexes: [<hosts_to_proxy_from>]   # only useful on http(s) mode
      wildcards: [<hosts_to_proxy_from>] # only useful on http(s) mode
```

Notes:

-   The `ip` is the local ip of the minion to proxy requests to
-   see localsettings_certbot for letsencrypt stuff
-   Frontends is a dictionnary of **ports / metadata** describing how
    to configure haproxy to proxy to the minion:

    - `mode` is node the **haproxy** mode but a switch for us to
      know how to proxy requests.

        http/https
        :   Proxy HTTP(s) requests, depending on an additionnal
            **regexes/wildcards/hosts** knob
        tcp/tcps
        :   configure a tcp based proxy, here
            **regexes/wildcards/hosts** is useless. Be warn,
            **main\_cert** will be the served ssl certicated as no
            SNI is possible
        redis
        :   configure a redis frontend (tcp based, so also no use
            of **regexes/wildcards/hosts**) based on
            <https://support.pivotal.io/hc/en-us/articles/205309388-How-to-setup-HAProxy-and-Redis-Sentinel-for-automatic-failover-between-Redis-Master-and-Slave-servers>

    - `to_port` can be used to override the port to proxy on the
      minion side if it is not the same that on haproxy side
    - If `frontends` are not specificied, you need to specify
      **ip** and one of **hosts/regexes/wildcards** as we default
      to configure http & https proxies.
    - If `frontends` are specified, you need to respecify all of
      them, no default will be used in this case.

-   80 & 443 frontend port modes default to respectivly http & https.
-   By default, if no frontends are specified, we setup http & https
    frontends. The SSL backend will try for forward first on 443, then
    on 80.
-   Acls order for http mode is not predictible yet and will be
    difficult. Prefer to use a sensible configuration for your case
    rather than complicating the ACLS generation algorythm.


### http
- HTTP proxies are the mostly used proxy
    - regexes
      :   list of regexeses to match either in the form
          - ``\[host\_regex``
          - ``[\[host\_regex, PATH\_URI\_regex\] (opt)]``
          - ``{host: \[host\_regex (opt), path PATH\_URI\_regex\] (opt)}``
          - [AT LEAST ONE of: ``host`` or ``path`` is required]
    -  wildcards
      :   list to strings which insensitive match if the
          header `HOST` endswith
    - hosts
      :   list to strings which insensitive match exactly
          the header `HOST`
    - letsencrypt (opt)
      :   bool, activate letsencrypt wellknown wrapper
    - letsencrypt_host  (opt)
      :   host for letsencrypt backend
    - letsencrypt_http_port (opt)
      :   port for letsencrypt backend (54080)
    - letsencrypt_tls_port (opt)
      :   TLS port for letsencrypt backend (54443)

if we want to proxy http to port "81" of myapp2-1 & https to 444

```yaml
corpusops_haproxy_registrations_registrations_haproxy1:
  - ip: 10.0.3.14
    hosts: [www.super.com]
    #( or regexes/wildcards)
    frontends:
      80:  {to_port: 81}
      443: {to_port: 444}
```

### http: host
If we have a minion haproxy1 and want to proxy to myapp2-1 on http &
https when a request targeting "www.super.com" arrise. all we have to do
is to:

- **ip can be a list !**

```yaml
corpusops_haproxy_registrations_registrations_haproxy1:
  - ip: 10.0.3.14
    hosts: [www.super.com]
```

#### http: wildcard
Wilcards are also supported via the wildcards key

```yaml
corpusops_haproxy_registrations_registrations_haproxy1:
  - ip: 10.0.3.14
    wildcards: ['*.www.super.com']
```

#### http: regex
regex is also supported via the regexes key

```yaml
corpusops_haproxy_registrations_registrations_haproxy1:
  - ip: 10.0.3.14
    regexes: ['my.*supemyappost.com']
corpusops_haproxy_registrations_registrations_haproxy1:
  - ip: 10.0.3.14
    regexes: [['my.*supemyappost.com', '^/api']]
corpusops_haproxy_registrations_registrations_haproxy1:
  - ip: 10.0.3.14
    regexes: [{host: 'my.*supemyappost.com', path: '^/api'}]
```

### SSL terminator / offloader
```yaml
corpusops_haproxy_registrations_registrations_haredis:
- hosts: ["foobar"]
  ip: "1.2.2.4"
  frontends:
    80:
      to_port: "180"
    443:
      to_port: "180"
      ssl_terminated: true
      # ssl_check: 'ssl verify none'
      # inter_check: 'inter 1s'
      # raw_srv: 'weight 100'
      # if backend is SSL, also try http if SSL port unavailable
      # if false, do not have the fallback (default: on)
      # http_fallback: false
      # if backend is SSL, also try http on this port
      # http_fallback_port: 80

# other exmaple with regex
corpusops_haproxy_registrations_registrations_haredis:
- regexes: [".*"]
  ip: "{{cops_zope_servers_ips}}"
  frontends:
    80:
      to_port: "180"
    443:
      to_port: "180"
      ssl_terminated: true

```

### redis
We have a special redis mode to do custom health checks on a redis cluster

Short form if you use the default port on both ends:

```yaml
corpusops_haproxy_registrations_registrations_haredis:
  - ip: 10.0.3.14 # localip of myapp2-1
    frontends:
      6378:  {}
```

Long forms

```yaml
corpusops_haproxy_registrations_registrations_haredis:
  - ip: 10.0.3.14
    frontends:
      66378: {to_port: 666, mode: redis}
      6378: {mode: redis}
```

#### Redis auth is supported this way

```yaml
corpusops_haproxy_registrations_registrations_haredis:
  - ip: 10.0.3.14
    frontends:
      6378: {password: "foobar", mode: redis}
```

### rabbitmq
We have a special rabbitmq mode to set sane options on backend for
rabbitmq Short form if you use the default port on both ends:

```yaml
corpusops_haproxy_registrations_registrations_haredis:
  - ip: 10.0.3.14
    frontends:
      5672:  {}
```

Long forms

```yaml
corpusops_haproxy_registrations_registrations_haredis:
  - ip: 10.0.3.14
    frontends:
      55672: {to_port: 333, mode: rabbitmq}
      5672: {mode: rabbitmq}
```

### Register 2 backends for one same frondend

```yaml
corpusops_haproxy_registrations_registrations_mc_cloud_http1:
   - "ip": "10.5.5.2"
     "hosts": ["es2.devhost5-1.local"]
     "frontends":
       "80":
         "mode": "http"
corpusops_haproxy_registrations_registrations_mc_cloud_http2:
   - "ip": "10.5.5.666"
     "hosts": ["es2.devhost5-2.local"]
     "frontends":
       "80":
         "mode": "http"
```

### Make a https to ssh proxy
``hosts`` needs a value but this wont "virtualhost" ssh. Only one ssh host is possible.

To register a proxy to ssh (from https) (eg: to bypass firewalls):

```yaml
- ssh_proxy: true
  # ssh_proxy_host: 127.0.0.1
  # ssh_proxy_port: 22
```

Then use this ssh slug to enjoy your proxy

```ssh
host AShortName
User <your_user>
HostName yourhost.net
Port 443
ProxyCommand openssl s_client -connect %h:%p -quiet
ServerAliveInterval 5
```

Then use
```sh
ssh yourhost.net
```

### Add raw opts
```yaml
- hosts: ["foobar"]
  # raw_frontend: []
  # raw_backend: []
```

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/haproxy_registrations/role.yml \
    --tags=vars,corpusops_vars,corpusops_haproxy_registrations_vars
```
