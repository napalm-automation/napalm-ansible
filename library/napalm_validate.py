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
        required: False
    username:
        description:
          - Username.
        required: False
    password:
        description:
          - Password.
        required: False
    dev_os:
        description:
          - OS of the device.
        required: False
        choices: ['eos', 'junos', 'iosxr', 'fortios', 'ibm', 'ios', 'nxos', 'panos', 'vyos']
    provider:
        description:
          - Dictionary which acts as a collection of arguments used to define the characteristics 
            of how to connect to the device.
            Note - hostname, username, password and dev_os must be defined in either provider 
            or local param
            Note - local param takes precedence, e.g. hostname is preferred to provider['hostname']
        required: False
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
          - YAML Validation file containing resources desired states.
        required: True
'''

EXAMPLES = '''
vars:
  ios_provider:
    hostname: "{{ inventory_hostname }}"
    username: "napalm"
    password: "napalm"
    dev_os: "ios"

 - name: GET VALIDATION REPORT
   napalm_validate:
    username: "{{ un }}"
    password: "{{ pwd }}"
    hostname: "{{ inventory_hostname }}"
    dev_os: "{{ dev_os }}"
    validation_file: validate.yml

 - name: GET VALIDATION REPORT USING PROVIDER
   napalm_validate:
    provider: "{{ ios_provider }}"
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


def get_device_instance(module, os_choices):

    provider = module.params['provider'] or {}

    # allow host or hostname
    provider['hostname'] = provider.get('hostname', None) or provider.get('host', None)
    # allow local params to override provider
    for param, pvalue in provider.items():
        if module.params.get(param) != False:
            module.params[param] = module.params.get(param) or pvalue

    hostname = module.params['hostname']
    username = module.params['username']
    dev_os = module.params['dev_os']
    password = module.params['password']
    timeout = module.params['timeout']

    argument_check = { 'hostname': hostname, 'username': username, 'dev_os': dev_os, 'password': password }
    for key, val in argument_check.items():
        if val is None:
            module.fail_json(msg=str(key) + " is required")

    # use checks outside of ansible defined checks, since params come can come from provider
    if dev_os not in os_choices:
        module.fail_json(msg="dev_os is not set to " + str(os_choices))

    optional_args = module.params['optional_args'] or {}
    try:
        network_driver = get_network_driver(dev_os)
        device = network_driver(hostname=hostname,
                                username=username,
                                password=password,
                                timeout=timeout,
                                optional_args=optional_args)
        device.open()
    except Exception as err:
        module.fail_json(msg="cannot connect to device: {0}".format(str(err)))
    return device


def main():
    os_choices = ['eos', 'junos', 'iosxr', 'fortios', 'ibm', 'ios', 'nxos', 'panos', 'vyos']
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(type='str', required=False, aliases=['host']),
            username=dict(type='str', required=False),
            password=dict(type='str', required=False, no_log=True),
            provider=dict(type='dict', required=False, no_log=True),
            dev_os=dict(type='str', required=False, choices=os_choices),
            timeout=dict(type='int', required=False, default=60),
            optional_args=dict(type='dict', required=False, default=None),
            validation_file=dict(type='str', required=True),
        ),
        supports_check_mode=False
    )
    if not napalm_found:
        module.fail_json(msg="the python module napalm is required")

    device = get_device_instance(module, os_choices)
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
