# ansible plugin to be fault tolerant for systemd docker containers

At build time systemd is not launched and all what we want is to
activate servies at boot time.

So in this case we wrap the ansible sytemd module and test
if systemd is launched.

In case of non availability, it will only disable/enable the service
via a symlink


