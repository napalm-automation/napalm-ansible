napalm-ansible
======

Collection of ansible modules that use [napalm](https://github.com/napalm-automation/napalm) to retrieve data or modify configuration on netwroking devices.

Modules
=======
The following modules are currenty available:
- napalm_get_bgp_config
- napalm_get_bgp_neighbors
- napalm_get_bgp_neighbors_detail
- napalm_get_environment
- napalm_get_facts
- napalm_get_interfaces
- napalm_get_interfaces_counters
- napalm_get_lldp_neighbors
- napalm_get_lldp_neighbors_detail
- napalm_install_config

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

Dependencies
=======
* [napalm](https://github.com/napalm-automation/napalm) 0.51.0 or later
