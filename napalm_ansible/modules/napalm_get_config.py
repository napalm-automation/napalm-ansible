"""
(c) 2018 Dmitry Zykov https://dmitryzykov.com
    Based on module napalm_install_conf by Elisa Jasinska <elisa@bigwaveit.org>
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
from ansible.module_utils.basic import AnsibleModule, return_values


DOCUMENTATION = '''
---
module: napalm_get_config
author: "Dmitry Zykov (@dmitryzykov)"
version_added: "1.0"
short_description: "Get and save to file config taken from a device supported by NAPALM"
description:
    - "This module will get configuration from a device with any
       OS supported by napalm and save it to a file."
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
    provider:
        description:
          - Dictionary which acts as a collection of arguments used to define the characteristics
            of how to connect to the device.
            Note - hostname, username, password and dev_os must be defined in either provider
            or local param
            Note - local param takes precedence, e.g. hostname is preferred to provider['hostname']
        required: False
    dev_os:
        description:
          - OS of the device
        required: False
        choices: ['eos', 'junos', 'iosxr', 'fortios', 'ios', 'mock', 'nxos', 'nxos_ssh', 'panos',
        'vyos']
    timeout:
        description:
          - Time in seconds to wait for the device to respond
        required: False
        default: 60
    optional_args:
        description:
          - Dictionary of additional arguments passed to underlying driver
        required: False
        default: None
    dest:
        description:
            - File where to save retreived configuration from device. Configuration won't be
              retrieved if not set.
        default: None
        required: True
    type:
        description:
            - Config type to retreive from device. If retrieved config is empty retrieve 
            "running" type instead.
        default: running
        required: False
        choices: ['running', 'candidate', 'startup']
'''

EXAMPLES = '''
- name: get running config
  napalm_get_config:
    hostname: "{{ inventory_hostname }}"
    username: "{{ username }}"
    dev_os: "{{ os }}"
    password: "{{ password }}"
    dest: "../backup/{{ inventory_hostname }}"
    type: running
    
- name: get startup config using provider
  napalm_get_config:
    provider: "{{ ios_provider }}"
    dest: "../backup/{{ inventory_hostname }}"
    type: startup
'''

RETURN = '''
changed:
    description: whether the config was retrieved and saved to file
    returned: always
    type: bool
    sample: True
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


def save_to_file(content, filename):
    f = open(filename, 'w')
    try:
        f.write(content)
    finally:
        f.close()


def main():
    os_choices = ['eos', 'junos', 'iosxr', 'fortios', 'ios', 'mock', 'nxos',
                  'nxos_ssh', 'panos', 'vyos', 'ros']
    config_types = ['running', 'candidate', 'startup']
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(type='str', required=False, aliases=['host']),
            username=dict(type='str', required=False),
            password=dict(type='str', required=False, no_log=True),
            provider=dict(type='dict', required=False),
            timeout=dict(type='int', required=False, default=60),
            optional_args=dict(required=False, type='dict', default=None),
            dev_os=dict(type='str', required=False, choices=os_choices),
            dest=dict(type='str', required=False, default=None),
            type=dict(type='str', required=False, choices=config_types, default="running"),
        ),
        supports_check_mode=True
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
    dest = module.params['dest']
    type = module.params['type']

    argument_check = {'hostname': hostname, 'username': username, 'dev_os': dev_os, 'dest': dest}
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
        config = device.get_config(retrieve=type)[type]
        # if retrieved config is empty retrieve "running" type instead
        if len(config) == 0:
            config = device.get_config(retrieve="running")["running"]
        save_to_file(config, dest)
        changed = True
    except Exception as e:
        module.fail_json(msg="cannot retrieve config:" + str(e))

    try:
        device.close()
    except Exception as e:
        module.fail_json(msg="cannot close device connection: " + str(e))

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()