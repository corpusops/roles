# corpusops.roles/services_backup_duplicity ansible role
## Documentation

backup using duplicity,

idea is to use backup profiles which

1. backup
2. cleanup everytime a while
3. generate a nagios-compatible probe for healthcheck

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/services_backup_duplicity/role.yml \
   -t corpusops.roles/services_backup_duplicity_vars
```

```yaml
# eg
corpusops_services_backup_duplicity_profiles: "{{corpusops_services_backup_duplicity_profiles_default}}"
```

## disclamer
- duplicity role was written initially for backuping both storage servers and burp2 backup servers on cloud, with gpg ENC. Thus you may need to create your owner profile (easy, just declare the profile in your inventory by duplicatif a default one).


## retention notes
- by default we take an initial full, for 3 month.
- we then make incrementals, with a retention of 15 days.


## reexecution protection notes
- duplicity will itself not run if already running
- we still add on the script something can kill everything if the backup ran for an excessive long time (default: 15days)
- the script will try to kill both the backup runner script (bash) and the children duplicity processes.
