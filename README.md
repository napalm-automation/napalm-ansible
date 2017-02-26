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
To install, clone napalm-ansible into your ansible playbook directory. For example:

```
mkdir ~/playbooks; cd playbooks
```

```
git clone https://github.com/napalm-automation/napalm-ansible.git
```

```
user@hostname:~/playbooks$ ls -la
total 12
drwxrwxr-x 3 user user 4096 Feb 26 12:51 .
drwxr-xr-x 7 user user 4096 Feb 26 12:49 ..
drwxrwxr-x 5 user user 4096 Feb 26 12:51 napalm-ansible
```
From here you would add your playbook for your project. It's very oftern we come to these tools needing to know how to run before we can walk.
Please review the [Ansible Documentation](http://docs.ansible.com/ansible/playbooks.html) as this will answer some basic questions.
It is also advised to have some kind of [yaml linter](https://pypi.python.org/pypi/yamllint) or syntax checker available. 

Dependencies
=======
* [napalm](https://github.com/napalm-automation/napalm) 1.00.0 or later


Examples
=======
Non parameterized example with comments to get you started
```
- name: Test Inventory #The Task Name
  hosts: cisco         #This will be in your ansible inventory file
  connection: local    #Required
  gather_facts: no     #Do not gather facts

  tasks:
    - name: get facts from device            #Task Name
      napalm_get_facts:                      #Call the napalm module, in this case napal_get_facts
        optional_args: {'secret': password}  #The enable password for Cisco IOS
        hostname: "{{ inventory_hostname }}" #This _is_ a parameter and is found in your ansible inventory file
        username: 'user'                     #The username to ssh with
        dev_os: 'ios'                        #The hardware operating system
        password: 'password'                 #The line level password
        filter: 'facts'                      #The list of items you want to retrieve. The filter keyword is _inclusive_ of what you want
      register: result                       #Ansible function for collecting output

    - name: print results                    #Task Name
      debug: msg="{{ result }}"              #Display the collected output
```

Keeping with our example dir at the beginning of the Readme, we now have this layout
```
user@host ~/playbooks
08:16 $ ls -la
total 32
drwxrwxr-x 3 user user 4096 Feb 26 07:24 .
drwxrwxr-x 8 user user 4096 Feb 25 16:32 ..
-rw-rw-r-- 1 user user  404 Feb 26 07:24 inventory.yaml
drwxrwxr-x 5 user user   75 Feb 23 00:40 napalm-ansible
```

You would run this playbook like so
```
cd ~/playbooks
```
```
ansible-playbook inventory.yaml -M napalm/library/
```

And it should produce output similar to this.

```
user@host$ ansible-playbook inventory.yaml -M napalm/library/

PLAY [Push config to switch group.] ********************************************

TASK [get facts from device] ***************************************************
ok: [192.168.0.11]

TASK [print results] *******************************************************************
ok: [192.168.0.11] => {
    "msg": {
        "ansible_facts": {
            "facts": {
                "fqdn": "router1.not set", 
                "hostname": "router1", 
                "interface_list": [
                    "FastEthernet0/0", 
                    "GigabitEthernet1/0", 
                    "GigabitEthernet2/0", 
                    "GigabitEthernet3/0", 
                    "GigabitEthernet4/0", 
                    "POS5/0", 
                    "POS6/0"
                ], 
                "model": "7206VXR", 
                "os_version": "7200 Software (C7200-ADVENTERPRISEK9-M), Version 15.2(4)S7, RELEASE SOFTWARE (fc4)", 
                "serial_number": "0123456789", 
                "uptime": 420, 
                "vendor": "Cisco"
            }
        }, 
        "changed": false
    }
}

PLAY RECAP *********************************************************************
192.168.0.11               : ok=2    changed=0    unreachable=0    failed=0
```

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