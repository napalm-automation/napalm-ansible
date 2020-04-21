# napalm-ansible

Collection of ansible modules that use [napalm](https://github.com/napalm-automation/napalm) to retrieve data or modify configuration on networking devices.

Modules
=======

The following modules are currently available:

- ``napalm_cli``
- ``napalm_diff_yang``
- ``napalm_get_facts``
- ``napalm_install_config``
- ``napalm_parse_yang``
- ``napalm_ping``
- ``napalm_translate_yang``
- ``napalm_validate``

Action-Plugins
=======

Action-Plugins should be used to make napalm-ansible more consistent with the behavior of other Ansible modules (eliminate the need of a provider and of individual task arguments for hostname, username, password, and timeout).

They provide default parameters for the hostname, username, password and timeout paramters.
* hostname is set to the first of provider {{ hostname }}, provider {{ host }}, play-context remote_addr.
* username is set to the first of provider {{ username }}, play-context connection_user.
* password is set to the first of provider {{ password }}, play-context password (-k argument).
* timeout is set to the provider {{ timeout }}, or else defaults to 60 seconds (can't be passed via command-line).

Install
=======

To install run either:

```
pip install napalm-ansible
pip install napalm
```

Or:

```
git clone https://github.com/napalm-automation/napalm-ansible
pip install napalm
```

Configuring Ansible
===================

Once you have installed ``napalm-ansible`` then you need to add napalm-ansible to your ``library`` and ``action_plugins`` paths in ``ansible.cfg``. If you used pip to install napalm-ansible, then you can just run the ``napalm-ansible`` command and follow the instructions specified there.

```
$ cat .ansible.cfg

[defaults]
library = ~/napalm-ansible/napalm_ansible/modules
action_plugins = ~/napalm-ansible/napalm_ansible/plugins/action
...

For more details on ansible's configuration file visit:
https://docs.ansible.com/ansible/latest/intro_configuration.html
```

Dependencies
=======
* [napalm](https://github.com/napalm-automation/napalm) 2.5.0 or later
* [ansible](https://github.com/ansible/ansible) 2.8.11 or later


Examples
=======

### Cisco IOS 

#### Inventory (IOS)

```INI
[cisco]
cisco1 ansible_host=cisco1.domain.com

[cisco:vars]
# Must match Python that NAPALM is installed into.
ansible_python_interpreter=/path/to/venv/bin/python
ansible_network_os=ios
ansible_connection=network_cli
ansible_user=admin
ansible_ssh_pass=my_password
```

#### Playbook (IOS)

```YAML
---
- name: NAPALM get_facts and get_interfaces
  hosts: cisco1
  gather_facts: False
  tasks:
    - name: napalm get_facts
      napalm_get_facts:
        filter: facts,interfaces

    - debug:
        var: napalm_facts
```

#### Playbook Output (IOS)

```INI
$ ansible-playbook napalm_get_ios.yml

PLAY [NAPALM get_facts and get_interfaces] *********

TASK [napalm get_facts] ****************************
ok: [cisco1]

TASK [debug] ***************************************
ok: [cisco5] => {
    "napalm_facts": {
        "fqdn": "cisco5.domain.com",
        "hostname": "cisco5",
        "interface_list": [
            "GigabitEthernet1",
            "GigabitEthernet2",
            "GigabitEthernet3",
            "GigabitEthernet4",
            "GigabitEthernet5",
            "GigabitEthernet6",
            "GigabitEthernet7"
        ],
        "model": "CSR1000V",
        "os_version": "Virtual XE Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 16.9.3, RELEASE SOFTWARE (fc2)",
        "serial_number": "9700000000P",
        "uptime": 13999500,
        "vendor": "Cisco"
    }
}

PLAY RECAP *****************************************
cisco1 : ok=2 changed=0 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0   

```


### Arista Inventory

```INI
[arista]
arista1 ansible_host=arista1.domain.com

[arista:vars]
# Must match Python that NAPALM is installed into.
ansible_python_interpreter=/path/to/venv/bin/python
ansible_network_os=eos
# Continue using 'network_cli' (NAPALM module itself will use eAPI)
ansible_connection=network_cli
```

### NX-OS Inventory

```INI
[nxos]
nxos1 ansible_host=nxos1.domain.com

[nxos:vars]
# Must match Python that NAPALM is installed into.
ansible_python_interpreter=/path/to/venv/bin/python
# NX-API port is specified in the playbook in 'optional_args'
# Use SSH by specifying 'dev_os: nxos_ssh' in task arguments
ansible_network_os=nxos
# Continue using 'network_cli' (NAPALM module itself will use NX-API)
ansible_connection=network_cli
ansible_user=admin
ansible_ssh_pass=my_password
```

### Junos Inventory

```INI
[juniper]
juniper1 ansible_host=juniper1.domain.com

[juniper:vars]
# Must match Python that NAPALM is installed into.
ansible_python_interpreter=/path/to/venv/bin/python
ansible_network_os=junos
# Continue using 'network_cli' (NAPALM module itself will use NETCONF)
ansible_connection=network_cli
ansible_user=admin
ansible_ssh_pass=my_password
```

Example to retrieve facts and interfaces from a device:

```YAML
---
- name: NAPALM get_facts and get_interfaces
  hosts: cisco1
  tasks:
    - name: Retrieve get_facts and get_interfaces
      napalm_get_facts:
        filter: facts,interfaces

    - debug:
        var: napalm_facts
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

Example to use default connection parameters:
```
 - name: get facts from device
   napalm_get_facts:
     dev_os: "{{ os }}"
     filter: facts,interfaces,bgp_neighbors
```
