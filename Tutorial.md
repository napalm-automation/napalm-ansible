
More Detailed Examples
=======

 It's very oftern we come to these tools needing to know how to run before we can walk.
Please review the [Ansible Documentation](http://docs.ansible.com/ansible/playbooks.html) as this will answer some basic questions.
It is also advised to have some kind of [yaml linter](https://pypi.python.org/pypi/yamllint) or syntax checker available. 

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
ansible-playbook inventory.yaml -M napalm-ansible/library/
```

And it should produce output similar to this.

```
user@host$ ansible-playbook inventory.yaml -M napalm-ansible/library/

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

Copyright 2016-present Nike, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.