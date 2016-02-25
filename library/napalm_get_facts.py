#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
(c) 2016 Elisa Jasinska <elisa@bigwaveit.org>

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
module: napalm_get_facts
author: "Elisa Jasinska (@fooelisa)"
version_added: "2.1.0"
short_description: "Gathers facts from a network device via napalm"
description:
    - "Gathers facts from a network device via the Python module napalm"
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
    filter:
        description:
            - A list of facts to retreive from a device and provided though C(ansible_facts)
              The following facts are available-
              facts, environment, interfaces, interfaces_counters, bgp_config, bgp_neighbors,
              bgp_neighbors_detail, lldp_neighbors, lldp_neighbors_detail
              Note- not all getters are implemented on all supported devcie types
        required: False
        default: 'facts'
'''

EXAMPLES = '''
 - name: get facts from device
   napalm_get_facts:
     hostname={{ inventory_hostname }}
     username={{ user }}
     dev_os={{ os }}
     password={{ passwd }}
     filter='facts'
   register: result

 - name: print data
   debug: var=result
'''

RETURN = '''
changed:
    description: "whether the command has been executed on the device"
    returned: always
    type: bool
    sample: True
ansible_facts:
    description: "Facts gathered on the device provided via C(ansible_facts)"
    returned: certain keys are returned depending on filter
    type: dict
'''

try:
    from napalm import get_network_driver
except ImportError:
    napalm_found = False
else:
    napalm_found = True

def main():
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(type='str', required=True),
            username=dict(type='str', required=True),
            password=dict(type='str', required=True, no_log=True),
            dev_os=dict(type='str', required=True, choices=['eos', 'junos', 'iosxr', 'fortios', 'ibm', 'ios', 'nxos']),
            timeout=dict(type='int', required=False, default=60),
            optional_args=dict(type='dict', required=False, default=None),
            filter=dict(type='str', required=False, default='facts'),

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
    filter_list = module.params['filter'].split(',')

    if module.params['optional_args'] is None:
        optional_args = {}
    else:
        optional_args = module.params['optional_args']

    # open device connection
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

    # retreive data from device
    facts = {}
    try:
        for filter in filter_list:
            if filter == 'facts':
                result = device.get_facts()
                facts['facts'] = result
            elif filter == 'interfaces':
                result = device.get_interfaces()
                facts['interfaces'] = result
            elif filter == 'interfaces_counter':
                result = device.get_interfaces_counter()
                facts['interfaces_counter'] = result
            elif filter == 'bgp_config':
                result = device.get_bgp_config()
                facts['bgp_config'] = result
            elif filter == 'bgp_neighbors':
                result = device.get_bgp_neighbors()
                facts['bgp_neighbors'] = result
            elif filter == 'bgp_neighbors_detail':
                result = device.get_bgp_neighbors_detail()
                facts['bgp_neighbors_detail'] = result
            elif filter == 'environment':
                result = device.get_environment()
                facts['environment'] = result
            elif filter == 'lldp_neighbors':
                result = device.get_lldp_neighbors()
                facts['lldp_neighbors'] = result
            elif filter == 'lldp_neighbors_detail':
                result = device.get_lldp_neighbors_detail()
                facts['lldp_neighbors_detail'] = result
            else:
                module.fail_json(msg="filter not recognized: " + filter)
    except:
        module.fail_json(msg="cannot retrieve device data")

    # close device connection
    try:
        device.close()
    except:
        module.fail_json(msg="cannot close device connection")

    module.exit_json(ansible_facts=facts)

# standard ansible module imports
from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
