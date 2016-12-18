napalm-ansible
======

Collection of ansible modules that use [napalm](https://github.com/napalm-automation/napalm) to retrieve data or modify configuration on netwroking devices.

Modules
=======
The following modules are currenty available:
- napalm_get_facts
- napalm_install_config
- napalm_validate

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
* [napalm](https://github.com/napalm-automation/napalm) 1.00.0 or later


Examples
=======
Example to retreive facts from a device
```
 - name: get facts from device
   napalm_get_facts:
     hostname={{ inventory_hostname }}
     username={{ user }}
     dev_os={{ os }}
     password={{ passwd }}
     filter='facts,interfaces,bgp_neighbors'
   register: result

 - name: print data
   debug: var=result
```
Example to install config on a device
```
- assemble:
    src=../compiled/{{ inventory_hostname }}/
    dest=../compiled/{{ inventory_hostname }}/running.conf

 - napalm_install_config:
    hostname={{ inventory_hostname }}
    username={{ user }}
    dev_os={{ os }}
    password={{ passwd }}
    config_file=../compiled/{{ inventory_hostname }}/running.conf
    commit_changes={{ commit_changes }}
    replace_config={{ replace_config }}
    get_diffs=True
    diff_file=../compiled/{{ inventory_hostname }}/diff
```

Example to get compliance report
```
- name: GET VALIDATION REPORT
  napalm_validate:
    username: "{{ un }}"
    password: "{{ pwd }}"
    hostname: "{{ inventory_hostname }}"
    dev_os: "{{ dev_os }}"
    validation_file: validate.yml
```