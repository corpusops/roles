# corpusops.roles/services_backup_restic ansible role
## Documentation

backup using restic,

idea is to use backup profiles which

1. backup
2. cleanup everytime a while
3. generate a nagios-compatible probe for healthcheck

## Role variables
To see variables for this role, call it directly via
```bash
ansible-playbook -l LIMIT -vvv roles/corpusops.roles/services_backup_restic/role.yml \
   -t corpusops.roles/services_backup_restic_vars
```

```yaml
# eg
corpusops_services_backup_restic_profiles: "{{corpusops_services_backup_restic_profiles_default}}"
```

## disclamer
- restic role was written initially for backuping both storage servers and burp2 backup servers on cloud, with gpg ENC. Thus you may need to create your owner profile (easy, just declare the profile in your inventory by duplicatif a default one).


## retention notes
- by default we take an initial full, for 3 month.
- we then make incrementals, with a retention of 15 days.


## reexecution protection notes
- restic will itself not run if already running
- we still add on the script something can kill everything if the backup ran for an excessive long time (default: 15days)
- the script will try to kill both the backup runner script (bash) and the children restic processes.

## how to init
- inspire yourself from the services_backup_restic_vars/defaults/main.yml comments:
- write or select the appropriate backup profiles
- set corpusops_services_backup_restic_selected_profiles
- think to set for earch profile in env_slug:
   - any env var needed for authentication like OS_* vars for openstack or FTP_PASSWORD for ftp/sftp.
   - BACKUP_DEST which is the url to backup to
