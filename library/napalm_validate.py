#!/usr/bin/python
# -*- coding: utf-8 -*-


DOCUMENTATION = '''
---
module: napalm_validate
author: Gabriele Gerbino (@GGabriele)
short_description: Performs deployment validation via napalm.
description:
    - Performs deployment validation via napalm.
requirements:
    - napalm
options:
    hostname:
        description:
          - IP or FQDN of the device you want to connect to.
        required: True
    username:
        description:
          - Username.
        required: True
    password:
        description:
          - Password.
        required: True
    dev_os:
        description:
          - OS of the device.
        required: True
        choices: ['eos', 'junos', 'iosxr', 'fortios', 'ibm', 'ios', 'nxos', 'panos']
    timeout:
        description:
          - Time in seconds to wait for the device to respond.
        required: False
        default: 60
    optional_args:
        description:
          - Dictionary of additional arguments passed to underlying driver.
        required: False
        default: None
    validation_file:
        description:
          - Validation file containing resources desired states.
        required: True
'''

EXAMPLES = '''
 - name: GET VALIDATION REPORT
   napalm_validate:
   username: "{{ un }}"
   password: "{{ pwd }}"
   hostname: "{{ inventory_hostname }}"
   dev_os: "{{ dev_os }}"
   validation_file: validate.yml
'''

RETURN = '''
changed:
    description: check to see if a change was made on the device.
    returned: always
    type: bool
    sample: false
compliance_report:
    description: validation report obtained via napalm.
    returned: always
    type: dict
'''

from ansible.module_utils.basic import *

try:
    from napalm_base import get_network_driver
except ImportError:
    napalm_found = False
else:
    napalm_found = True


def get_compliance_report(module, device):
    return device.compliance_report(module.params['validation_file'])


def get_device_instance(module):
    optional_args = module.params['optional_args'] or {}
    try:
        network_driver = get_network_driver(module.params['dev_os'])
        device = network_driver(hostname=module.params['hostname'],
                                username=module.params['username'],
                                password=module.params['password'],
                                timeout=module.params['timeout'],
                                optional_args=optional_args)
        device.open()
    except Exception as err:
        module.fail_json(msg="cannot connect to device: {0}".format(str(err)))
    return device


def main():
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(type='str', required=True),
            username=dict(type='str', required=True),
            password=dict(type='str', required=True, no_log=True),
            dev_os=dict(type='str', required=True, choices=['eos', 'junos', 'iosxr', 'fortios', 'ibm', 'ios', 'nxos', 'panos']),
            timeout=dict(type='int', required=False, default=60),
            optional_args=dict(type='dict', required=False, default=None),
            validation_file=dict(type='str', required=True),
        ),
        supports_check_mode=False
    )
    if not napalm_found:
        module.fail_json(msg="the python module napalm is required")

    device = get_device_instance(module)
    compliance_report = get_compliance_report(module, device)

    # close device connection
    try:
        device.close()
    except Exception as err:
        module.fail_json(msg="cannot close device connection: {0}".format(str(err)))

    results = {}
    results['compliance_report'] = compliance_report
    module.exit_json(**results)


if __name__ == '__main__':
    main()
