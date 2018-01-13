# corpusops.roles/ssl_ca_signed_cert ansible role

## Documentation

Managment of ssl certs signed by a local authority

It take care of creating an auth, an intermediate and
signing a csr for the given CN making a new cert available.

### usage

- see [test](./test.yml)


## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/ssl_ca_signed_cert/role.yml \
    --tags=vars,corpusops_vars,corpusops_ssl_ca_signed_cert_vars
```
