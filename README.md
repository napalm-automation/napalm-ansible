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
cisco5 ansible_host=cisco5.domain.com

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
  hosts: cisco5
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
ok: [cisco5]

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
        "os_version": "Virtual XE Software, Version 16.9.3, RELEASE SOFTWARE (fc2)",
        "serial_number": "9700000000P",
        "uptime": 13999500,
        "vendor": "Cisco"
    }
}

PLAY RECAP *****************************************
cisco5 : ok=2 changed=0 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0   

```

### Arista EOS

#### Inventory (EOS)

```INI
[arista]
arista5 ansible_host=arista5.domain.com

[arista:vars]
# Must match Python that NAPALM is installed into.
ansible_python_interpreter=/path/to/venv/bin/python
ansible_network_os=eos
# Continue using 'network_cli' (NAPALM module itself will use eAPI)
ansible_connection=network_cli
ansible_user=admin
ansible_ssh_pass=my_password
```

#### Playbook (EOS)

```YAML
---
- name: NAPALM get_facts and get_interfaces
  hosts: arista5
  gather_facts: False
  tasks:
    - name: napalm get_facts
      napalm_get_facts:
        filter: facts,interfaces

    - debug:
        var: napalm_facts
```

#### Playbook Output (EOS)

```INI
$ ansible-playbook napalm_get_arista.yml

PLAY [NAPALM get_facts and get_interfaces] *********

TASK [napalm get_facts] ****************************
ok: [arista5]

TASK [debug] ***************************************
ok: [arista5] => {
    "napalm_facts": {
        "fqdn": "arista5",
        "hostname": "arista5",
        "interface_list": [
            "Ethernet1",
            "Ethernet2",
            "Ethernet3",
            "Ethernet4",
            "Ethernet5",
            "Ethernet6",
            "Ethernet7",
            "Management1",
            "Vlan1"
        ],
        "model": "vEOS",
        "os_version": "4.20.10M-10040268.42010M",
        "serial_number": "",
        "uptime": 12858220,
        "vendor": "Arista"
    }
}

PLAY RECAP ****************************************
arista5 : ok=2 changed=0 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0   
```

### Cisco NX-OS

#### Inventory (NX-OS)

```INI
[nxos]
nxos1 ansible_host=nxos1.domain.com

[nxos:vars]
# Must match Python that NAPALM is installed into.
ansible_python_interpreter=/path/to/venv/bin/python
ansible_network_os=nxos
# Continue using 'network_cli' (NAPALM module itself will use NX-API)
ansible_connection=network_cli
ansible_user=admin
ansible_ssh_pass=my_password
```

#### Playbook (NX-OS NX-API)

```YAML
---
- name: napalm 
  hosts: nxos1
  gather_facts: False
  tasks:
    - name: Retrieve get_facts, get_interfaces
      napalm_get_facts:
        filter: facts,interfaces
        # Specify NX-API Port
        optional_args:
          port: 8443

    - debug:
        var: napalm_facts
```

#### Playbook Output (NX-OS NX-API)

```INI
$ ansible-playbook napalm_get_nxos.yml

PLAY [napalm] ***************************************

TASK [Retrieve get_facts, get_interfaces] ***********
ok: [nxos1]

TASK [debug] ****************************************
ok: [nxos1] => {
    "napalm_facts": {
        "fqdn": "nxos1.domain.com",
        "hostname": "nxos1",
        "interface_list": [
            "mgmt0",
            "Ethernet1/1",
            "Ethernet1/2",
            "Ethernet1/3",
            "Ethernet1/4",
            "Vlan1"
        ],
        "model": "Nexus9000 9000v Chassis",
        "os_version": "",
        "serial_number": "9B00000000S",
        "uptime": 12767664,
        "vendor": "Cisco"
    }
}

PLAY RECAP ******************************************
nxos1 : ok=2 changed=0 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0   
```

#### Playbook (NX-OS SSH)

```YAML
---
- name: napalm nxos_ssh
  hosts: nxos1
  tasks:
    - name: Retrieve get_facts, get_interfaces
      napalm_get_facts:
        filter: facts,interfaces
        # Instruct NAPALM module to use SSH
        dev_os: nxos_ssh

    - debug:
        var: napalm_facts
```

#### Playbook Output (NX-OS SSH)

```INI
$ ansible-playbook napalm_get_nxos_ssh.yml

PLAY [napalm nxos_ssh] ********************************

TASK [Retrieve get_facts, get_interfaces] *************
ok: [nxos1]

TASK [debug] ******************************************
ok: [nxos1] => {
    "napalm_facts": {
        "fqdn": "nxos1.domain.com",
        "hostname": "nxos1",
        "interface_list": [
            "mgmt0",
            "Ethernet1/1",
            "Ethernet1/2",
            "Ethernet1/3",
            "Ethernet1/4",
            "Vlan1"
        ],
        "model": "Nexus9000 9000v Chassis",
        "os_version": "9.2(3)",
        "serial_number": "9000000000S",
        "uptime": 12767973,
        "vendor": "Cisco"
    }
}

PLAY RECAP ********************************************
nxos1 : ok=3 changed=0 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0   
```

### Juniper Junos

#### Inventory (Junos)

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

#### Playbook (Junos)

```YAML
---
- name: napalm 
  hosts: juniper
  gather_facts: False
  tasks:
    - name: Retrieve get_facts, get_interfaces
      napalm_get_facts:
        filter: facts,interfaces

    - debug:
        var: napalm_facts
```

#### Playbook Output (Junos)

```INI
$ ansible-playbook napalm_get_junos.yml -i

PLAY [napalm] *****************************************

TASK [Retrieve get_facts, get_interfaces] *************
ok: [juniper1]

TASK [debug] ******************************************
ok: [juniper1] => {
    "napalm_facts": {
        "fqdn": "juniper1",
        "hostname": "juniper1",
        "interface_list": [
            "fe-0/0/0",
            "gr-0/0/0",
            "ip-0/0/0",
            "lt-0/0/0",
            "mt-0/0/0",
            "sp-0/0/0",
            "fe-0/0/1",
            "fe-0/0/2",
            "fe-0/0/3",
            "fe-0/0/4",
            "fe-0/0/5",
            "fe-0/0/6",
            "fe-0/0/7",
            "gre",
            "ipip",
            "irb",
            "lo0",
            "lsi",
            "mtun",
            "pimd",
            "pime",
            "pp0",
            "ppd0",
            "ppe0",
            "st0",
            "tap",
            "vlan"
        ],
        "model": "SRX100H2",
        "os_version": "12.1X44-D35.5",
        "serial_number": "BZ0000000008",
        "uptime": 119586097,
        "vendor": "Juniper"
    }
}

PLAY RECAP *******************************************
juniper1 : ok=2 changed=0 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0   
```

### Example to install config on a device

```INI
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

### Example to get compliance report

```YAML
- name: GET VALIDATION REPORT
  napalm_validate:
    username: "{{ user }}"
    password: "{{ passwd }}"
    hostname: "{{ inventory_hostname }}"
    dev_os: "{{ dev_os }}"
    validation_file: validate.yml
```

