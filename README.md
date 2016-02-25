napalm-ansible
======

Collection of ansible modules that use [napalm](https://github.com/napalm-automation/napalm) to retrieve data or modify configuration on netwroking devices.

Install
=======
To install, clone the library directory into your ansible path.

OR

Add the following in requirements.yml
```
- src: https://github.com/napalm-automation/napalm-ansible/
  version: master
  name: napalm
  path: roles
```
Then execute:
```
ansible-galaxy install -r requirements.yml --force
```

