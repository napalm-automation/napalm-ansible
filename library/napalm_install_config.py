#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
(c) 2016 Elisa Jasinska <elisa@bigwaveit.org>
    Original prototype by David Barroso <dbarrosop@dravetech.com>

This file is part of Ansible

Ansible is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Ansible is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
"""

DOCUMENTATION = '''
---
module: napalm_install_config
author: "Elisa Jasinska (@fooelisa)"
version_added: "2.1.0"
short_description: "Installs the configuration taken from a file on a device supported by NAPALM"
description:
    - "This library will take the configuration from a file and load it into a device running any OS supported by napalm.
      The old configuration will be replaced or merged with the new one."
requirements:
    - napalm
options:
    hostname:
        description:
          - IP or FQDN of the device you want to connect to
        required: True
    username:
        description:
          - Username
        required: True
    password:
        description:
          - Password
        required: True
    dev_os:
        description:
          - OS of the device
        required: True
        choices: ['eos', 'junos', 'iosxr', 'fortios', 'ibm', 'ios', 'nxos']
    timeout:
        description:
          - Time in seconds to wait for the device to respond
        required: False
        default: 60
    optional_args:
        description:
          - Dictionary of additional arguments passed to underlying driver
        required: False
    config_file:
        description:
          - Path to the file to load the configuration from
        required: True
    commit_changes:
        description:
          - If set to True the configuration will be actually merged or replaced. If the set to False,
            we will not apply the changes, just check and report the diff
        required: True
    replace_config:
        description:
          - If set to True, the entire configuration on the device will be replaced during the commit.
            If set to False, we will merge the new config with the existing one. Default- False
        choices: [yes,on,1,true,no,off,0,false]
        default: False
        required: False
    diff_file:
        description:
          - A path to the file where we store the "diff" between the running configuration and the new
            configuration. If not set the diff between configurations will not be saved.
        default: None
        required: False
    get_diffs:
        description:
            - Set to False to not have any diffs generated. Useful if platform does not support commands
              being used to generate diffs. Note- By default diffs are generated even if the diff_file
              param is not set.
        choices: [yes,on,1,true,no,off,0,false]
        default: True
        required: False
'''

EXAMPLES = '''
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
'''

RETURN = '''
changed:
    description: whether the config on the device was changed
    returned: always
    type: bool
    sample: True
msg:
    description: diff of the change
    returned: always
    type: string
    sample: "[edit system]\n-  host-name lab-testing;\n+  host-name lab;"
'''

try:
    from napalm import get_network_driver
except ImportError:
    napalm_found = False
else:
    napalm_found = True

def save_to_file(content, filename):
    f = open(filename, 'w')
    try:
        f.write(content)
    finally:
        f.close()

def main():
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(type='str', required=True),
            username=dict(type='str', required=True),
            password=dict(type='str', required=True),
            timeout=dict(type='int', required=False, default=60),
            optional_args=dict(required=False, type='dict', default=None),
            config_file=dict(type='str', required=True),
            dev_os=dict(type='str', required=True, choices=['eos', 'junos', 'iosxr', 'fortios', 'ibm', 'ios', 'nxos']),
            commit_changes=dict(type='bool', required=True, choices=BOOLEANS),
            replace_config=dict(type='bool', required=False, choices=BOOLEANS, default=False),
            diff_file=dict(type='str', required=False, default=None),
            get_diffs=dict(type='bool', required=False, choices=BOOLEANS, default=True)
        ),
        supports_check_mode=True
    )

    if not napalm_found:
        module.fail_json(msg="the python module napalm is required")

    hostname = module.params['hostname']
    username = module.params['username']
    dev_os = module.params['dev_os']
    password = module.params['password']
    timeout = module.params['timeout']
    config_file = module.params['config_file']
    commit_changes = module.params['commit_changes']
    replace_config = module.params['replace_config']
    diff_file = module.params['diff_file']
    get_diffs = module.params['get_diffs']

    if module.params['optional_args'] is None:
        optional_args = {}
    else:
        optional_args = module.params['optional_args']

    try:
        network_driver = get_network_driver(dev_os)
        device = network_driver(hostname=hostname,
                                username=username,
                                password=password,
                                timeout=timeout,
                                optional_args=optional_args)
        device.open()
    except:
        module.fail_json(msg="cannot connect to device")

    try:
        if replace_config:
            device.load_replace_candidate(filename=config_file)
        else:
            device.load_merge_candidate(filename=config_file)
    except:
        module.fail_json(msg="cannot load config")

    try:
        if get_diffs:
            diff = device.compare_config().encode('utf-8')
            changed = len(diff) > 0
        else:
            changed = True
            diff = None
        if diff_file is not None and get_diffs:
            save_to_file(diff, diff_file)
    except:
        module.fail_json(msg="cannot diff config")

    try:
        if module.check_mode or not commit_changes:
            device.discard_config()
        else:
            if changed:
                device.commit_config()
    except:
        module.fail_json(msg="cannot install config")

    try:
        device.close()
    except:
        module.fail_json(msg="cannot close device connection")

    module.exit_json(changed=changed, msg=diff)

# standard ansible module imports
from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
