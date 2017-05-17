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
To install, clone napalm-ansible into your ansible module path. This will depend on your own setup and contents of your ansible.cfg file. If yours looks like:

```
[defaults]
library = ~/workspace/napalm-ansible
```
Then you can do the following:

```
cd ~/workspace
```

```
git clone https://github.com/napalm-automation/napalm-ansible.git
```

```
user@hostname:~/workspace ls -la
total 12
drwxrwxr-x 3 user user 4096 Feb 26 12:51 .
drwxr-xr-x 7 user user 4096 Feb 26 12:49 ..
drwxrwxr-x 5 user user 4096 Feb 26 12:51 napalm-ansible
```
From here you would add your playbook(s) for your project, for example:

```
mkdir ansible-playbooks

user@hostname:~/workspace ls -la
total 12
drwxrwxr-x 3 user user 4096 Feb 26 12:51 .
drwxr-xr-x 7 user user 4096 Feb 26 12:49 ..
drwxrwxr-x 5 user user 4096 Feb 26 12:51 napalm-ansible
drwxrwxr-x 5 user user 4096 Feb 26 12:53 ansible-playbooks
```

Dependencies
=======
* [napalm](https://github.com/napalm-automation/napalm) 1.00.0 or later

Examples
=======
Example to retrieve facts from a device
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