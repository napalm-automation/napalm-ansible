from ansible.module_utils.basic import AnsibleModule, return_values


DOCUMENTATION = '''
---
module: napalm_cli
author: "Charlie Allom - based on napalm_ping Jason Edelman (@jedelman8)"
version_added: "2.2"
short_description: "Executes CLI commands and returns response using NAPALM"
description:
    - "This module logs into the device, issues a ping request, and returns the response"
requirements:
    - napalm
options:
    hostname:
        description:
          - IP or FQDN of the device you want to connect to
        required: False
    username:
        description:
          - Username
        required: False
    password:
        description:
          - Password
        required: False
    args:
        description:
          - Keyword arguments to pass to the `cli` method
        required: True
    dev_os:
        description:
          - OS of the device
        required: False
        choices: ['eos', 'junos', 'iosxr', 'fortios', 'ios', 'mock', 'nxos', 'nxos_ssh', 'panos',
        'vyos']
    provider:
        description:
          - Dictionary which acts as a collection of arguments used to define the characteristics
            of how to connect to the device.
            Note - hostname, username, password and dev_os must be defined in either provider
            or local param
            Note - local param takes precedence, e.g. hostname is preferred to provider['hostname']
        required: False

'''

EXAMPLES = '''
- napalm_cli:
    hostname: "{{ inventory_hostname }}"
    username: "napalm"
    password: "napalm"
    dev_os: "eos"
    args:
        commands:
            - show version
            - show snmp chassis

- napalm_cli:
    provider: "{{ napalm_provider }}"
    args:
        commands:
            - show version
            - show snmp chassis
'''

RETURN = '''
changed:
    description: ALWAYS RETURNS FALSE
    returned: always
    type: bool
    sample: True
results:
    description: string of command output
    returned: always
    type: dict
    sample: '{
        "show snmp chassis": "Chassis: 1234\n",
        "show version": "Arista vEOS\nHardware version:    \nSerial number:       \nSystem MAC address:  0800.27c3.5f28\n\nSoftware image version: 4.17.5M\nArchitecture:           i386\nInternal build version: 4.17.5M-4414219.4175M\nInternal build ID:      d02143c6-e42b-4fc3-99b6-97063bddb6b8\n\nUptime:                 1 hour and 21 minutes\nTotal memory:           1893416 kB\nFree memory:            956488 kB\n\n"  # noqa
    }'
'''

napalm_found = False
try:
    from napalm import get_network_driver
    napalm_found = True
except ImportError:
    pass

# Legacy for pre-reunification napalm (remove in future)
if not napalm_found:
    try:
        from napalm_base import get_network_driver   # noqa
        napalm_found = True
    except ImportError:
        pass


def main():
    os_choices = ['eos', 'junos', 'iosxr', 'fortios',
                  'ios', 'mock', 'nxos', 'nxos_ssh', 'panos', 'vyos', 'ros']
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(type='str', required=False, aliases=['host']),
            username=dict(type='str', required=False),
            password=dict(type='str', required=False, no_log=True),
            provider=dict(type='dict', required=False),
            timeout=dict(type='int', required=False, default=60),
            dev_os=dict(type='str', required=False, choices=os_choices),
            optional_args=dict(required=False, type='dict', default=None),
            args=dict(required=True, type='dict', default=None),
        ),
        supports_check_mode=False
    )

    if not napalm_found:
        module.fail_json(msg="the python module napalm is required")

    provider = module.params['provider'] or {}

    no_log = ['password', 'secret']
    for param in no_log:
        if provider.get(param):
            module.no_log_values.update(return_values(provider[param]))
        if provider.get('optional_args') and provider['optional_args'].get(param):
            module.no_log_values.update(return_values(provider['optional_args'].get(param)))
        if module.params.get('optional_args') and module.params['optional_args'].get(param):
            module.no_log_values.update(return_values(module.params['optional_args'].get(param)))

    # allow host or hostname
    provider['hostname'] = provider.get('hostname', None) or provider.get('host', None)
    # allow local params to override provider
    for param, pvalue in provider.items():
        if module.params.get(param) is not False:
            module.params[param] = module.params.get(param) or pvalue

    hostname = module.params['hostname']
    username = module.params['username']
    dev_os = module.params['dev_os']
    password = module.params['password']
    timeout = module.params['timeout']
    args = module.params['args']

    argument_check = {'hostname': hostname, 'username': username, 'dev_os': dev_os}
    for key, val in argument_check.items():
        if val is None:
            module.fail_json(msg=str(key) + " is required")

    # use checks outside of ansible defined checks, since params come can come from provider
    if dev_os not in os_choices:
        module.fail_json(msg="dev_os is not set to " + str(os_choices))

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
    except Exception as e:
        module.fail_json(msg="cannot connect to device: " + str(e))

    try:
        cli_response = device.cli(**args)
    except Exception as e:
        module.fail_json(msg="{}".format(e))

    try:
        device.close()
    except Exception as e:
        module.fail_json(msg="cannot close device connection: " + str(e))

    module.exit_json(changed=False, results=cli_response)


if __name__ == '__main__':
    main()
