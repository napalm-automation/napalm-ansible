"""
(c) 2017 David Barroso <dbarrosop@dravetech.com>

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
# standard ansible module imports
from ansible.module_utils.basic import AnsibleModule, return_values

import json

napalm_found = False
try:
    from napalm import get_network_driver
    napalm_found = True
except ImportError:
    pass

# Legacy for pre-reunification napalm (remove in future)
if not napalm_found:
    try:
        from napalm_base import get_network_driver    # noqa
        napalm_found = True
    except ImportError:
        pass

try:
    import napalm_yang
except ImportError:
    napalm_yang = None


DOCUMENTATION = '''
---
module: napalm_parse_yang
author: "David Barroso (@dbarrosop)"
version_added: "0.0"
short_description: "Parse native config/state from a file or device."
description:
    - "Parse configuration/state from a file or device and returns a dict that"
    - "represents a valid YANG object."
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
    dev_os:
        description:
          - OS of the device
        required: False
        choices: ['eos', 'junos', 'iosxr', 'fortios', 'ios', 'mock',
                  'nxos', 'nxos_ssh', 'panos', 'vyos']
    provider:
        description:
          - Dictionary which acts as a collection of arguments used to define
            the characteristics of how to connect to the device.
            Note - hostname, username, password and dev_os must be defined in
              either provider or local param if we want to parse from a device
            Note - local param takes precedence, e.g. hostname is preferred to
              provider['hostname']
        required: False
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
    file_path:
        description:
          - "Path to a file to load native config/state from.
            Note: Either file_path or data to connect to a device must be
              provided.
            Note: file_path takes precedence over a live device"
        required: False
        defaut: None
    mode:
        description:
          - "Whether to parse config/state or both.
            Note: `both` is not supported in combination with `file_path`."
        required: True
        choices: ['config', 'state', 'both']
    models:
        description:
          - A list that should match the SUPPORTED_MODELS in napalm-yang
        required: True
        choices: ""
    profiles:
        description:
          - A list profiles
        required: False
        choices: ""
'''

EXAMPLES = '''
- name: Parse from device
  napalm_parse_yang:
    hostname: '{{ inventory_hostname }}'
    username: '{{ user }}'
    dev_os: '{{ os }}'
    password: '{{ passwd }}'
    mode: "config"
    profiles: ["eos"]
    models:
        - models.openconfig_interfaces
  register: running

- name: Parse from file
  napalm_parse_yang:
    file_path: "eos.config"
    mode: "config"
    profiles: ["eos"]
    models:
        - models.openconfig_interfaces
  register: config
'''

RETURN = '''
changed:
  description: "Dict the representes a valid YANG object"
  returned: always
  type: dict
  sample: "{'interfaces': {'interface':'Et1': {...}, ... }}"
'''


def update_module_provider_data(module):
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
    provider['hostname'] = provider.get('hostname', None) \
        or provider.get('host', None)
    # allow local params to override provider
    for param, pvalue in provider.items():
        if module.params.get(param) is not False:
            module.params[param] = module.params.get(param) or pvalue


def get_root_object(models):
    """
    Read list of models and returns a Root object with the proper models added.
    """
    root = napalm_yang.base.Root()

    for model in models:
        current = napalm_yang
        for p in model.split("."):
            current = getattr(current, p)
        root.add_model(current)

    return root


def parse_from_file(module):
    file_path = module.params["file_path"]
    models = module.params["models"]
    mode = module.params["mode"]
    profiles = module.params["profiles"]

    root = get_root_object(models)

    with open(file_path, "r") as f:
        native = f.read()
        try:
            native = json.loads(native)
        except ValueError:
            native = [native]

    if mode == "config":
        root.parse_config(native=native, profile=profiles)
    elif mode == "state":
        root.parse_state(native=native, profile=profiles)
    else:
        module.fail_json(
            msg="You can't parse both at the same time from a file")
    return root


def parse_from_device(module, os_choices):
    update_module_provider_data(module)

    hostname = module.params['hostname']
    username = module.params['username']
    password = module.params['password']
    timeout = module.params['timeout']
    models = module.params['models']
    mode = module.params['mode']
    profiles = module.params['profiles']

    dev_os = module.params['dev_os']
    argument_check = {'hostname': hostname, 'username': username, 'dev_os': dev_os}
    for key, val in argument_check.items():
        if val is None:
            module.fail_json(msg=str(key) + " is required")

    # use checks outside of ansible defined checks, since params come can come
    # from provider
    dev_os = module.params['dev_os']
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
        module.fail_json(msg="cannot connect to device: {}".format(e))

    root = get_root_object(models)

    if mode in ["config", "both"]:
        root.parse_config(device=device, profile=profiles or device.profile)

    if mode in ["state", "both"]:
        root.parse_state(device=device, profile=profiles or device.profile)

    # close device connection
    try:
        device.close()
    except Exception as e:
        module.fail_json(msg="cannot close device connection: {}".format(e))

    return root


def main():
    os_choices = ['eos', 'junos', 'iosxr', 'fortios', 'ios',
                  'mock', 'nxos', 'nxos_ssh', 'panos', 'vyos']
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(type='str', required=False, aliases=['host']),
            username=dict(type='str', required=False),
            password=dict(type='str', required=False, no_log=True),
            provider=dict(type='dict', required=False),
            file_path=dict(type='str', required=False),
            mode=dict(type='str', required=True,
                      choices=["config", "state", "both"]),
            models=dict(type="list", required=True),
            profiles=dict(type="list", required=False),
            dev_os=dict(type='str', required=False, choices=os_choices),
            timeout=dict(type='int', required=False, default=60),
            optional_args=dict(type='dict', required=False, default=None),

        ),
        supports_check_mode=True
    )

    if not napalm_found:
        module.fail_json(msg="the python module napalm is required")
    if not napalm_yang:
        module.fail_json(msg="the python module napalm-yang is required")

    if module.params["file_path"]:
        yang_model = parse_from_file(module)
    else:
        yang_model = parse_from_device(module, os_choices)

    module.exit_json(yang_model=yang_model.to_dict(filter=True))


if __name__ == '__main__':
    main()
