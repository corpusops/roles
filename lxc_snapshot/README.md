# corpusops.lxc_snapshot ansible role
## Documentation
Remove and impersonate a lxc container from running personnal bits (ssh keys and etc)
See [templates/bin/cops_container_snapshot.sh](./templates/bin/cops_container_snapshot.sh)

You d better use this [corpusops playbook](https://github.com/corpusops/playbooks/blob/master/provision/lxc_container/snapshot.yml) that makes a snapshot container
from a running container
```
bin/ansible-playbook -i superhost, playbooks/corpusops/provision/lxc_container/snapshot.yml  -e "container=lxcmakinastates image=gitlabrunner"
```

Where:
- container: original container
- image: snapshotted container to create or update
