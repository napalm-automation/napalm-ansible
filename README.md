# napalm-ansible

Collection of ansible modules that use [napalm](https://github.com/napalm-automation/napalm) to retrieve data or modify configuration on networking devices.

Modules
=======

The following modules are currently available:

- ``napalm_diff_yang``
- ``napalm_get_facts``
- ``napalm_install_config``
- ``napalm_parse_yang``
- ``napalm_ping``
- ``napalm_translate_yang``
- ``napalm_validate``

Install
=======

To install just run the command:

```
pip install napalm-ansible
```

Configuring ansible
===================

Once you have installed ``napalm-ansible`` run the command ``napalm-ansible`` and follow the instructions. For example::

```
$ napalm-ansible
To make sure ansible can make use of the napalm modules you will have
to add the following configurtion to your ansible configureation
file, i.e. `./ansible.cfg`:

    [defaults]
    library = /Users/dbarroso/workspace/napalm/napalm-ansible/napalm_ansible

For more details on ansible's configuration file visit:
https://docs.ansible.com/ansible/latest/intro_configuration.html
```

Dependencies
=======
* [napalm](https://github.com/napalm-automation/napalm) 1.00.0 or later
* [ansible](https://github.com/ansible/ansible) 2.2.0.0 or later


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
