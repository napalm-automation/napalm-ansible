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
from ansible.module_utils.basic import AnsibleModule, return_values


DOCUMENTATION = '''
---
module: napalm_get_facts
author: "Elisa Jasinska (@fooelisa)"
version_added: "2.1"
short_description: "Gathers facts from a network device via napalm"
description:
    - "Gathers facts from a network device via the Python module napalm"
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
    ignore_notimplemented:
        description:
          - "Ignores NotImplementedError for filters which aren't supported by the driver. Returns
            invalid filters in a list called: not_implemented"
        required: False
        default: False
        choices: [True, False]
    filter:
        description:
            - "A list of facts to retreive from a device and provided though C(ansible_facts)
              The list of facts available are maintained at:
                  http://napalm.readthedocs.io/en/latest/support/
              Note- not all getters are implemented on all supported device types"
        required: False
        default: ['facts']
    args:
        description:
            - dictionary of kwargs arguments to pass to the filter. The outer key is the name of
              the getter (same as the filter)
        required: False
        default: None
'''

EXAMPLES = '''
- name: get facts from device
  napalm_get_facts:
    hostname: '{{ inventory_hostname }}'
    username: '{{ user }}'
    dev_os: '{{ os }}'
    password: '{{ passwd }}'
    filter: ['facts']
  register: result

- name: print data
  debug:
    var: result

- name: Getters
  napalm_get_facts:
    provider: "{{ ios_provider }}"
    filter:
      - "lldp_neighbors_detail"
      - "interfaces"

- name: get facts from device
  napalm_get_facts:
    hostname: "{{ host }}"
    username: "{{ user }}"
    dev_os: "{{ os }}"
    password: "{{ password }}"
    optional_args:
      port: "{{ port }}"
    filter: ['facts', 'route_to', 'interfaces']
    args:
        route_to:
            protocol: static
            destination: 8.8.8.8

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

napalm_found = False
try:
    from napalm import get_network_driver
    napalm_found = True
except ImportError:
    pass

# Legacy for pre-reunification napalm (remove in future)
if not napalm_found:
    try:
        from napalm_base import get_network_driver     # noqa
        napalm_found = True
    except ImportError:
        pass


def main():
    os_choices = ['eos', 'junos', 'iosxr', 'fortios', 'ios', 'mock', 'nxos', 'nxos_ssh', 'panos',
                  'vyos', 'ros']
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(type='str', required=False, aliases=['host']),
            username=dict(type='str', required=False),
            password=dict(type='str', required=False, no_log=True),
            provider=dict(type='dict', required=False),
            dev_os=dict(type='str', required=False, choices=os_choices),
            timeout=dict(type='int', required=False, default=60),
            ignore_notimplemented=dict(type='bool', required=False, default=False),
            args=dict(type='dict', required=False, default=None),
            optional_args=dict(type='dict', required=False, default=None),
            filter=dict(type='list', required=False, default=['facts']),

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
    filter_list = module.params['filter']
    args = module.params['args'] or {}
    ignore_notimplemented = module.params['ignore_notimplemented']
    implementation_errors = []

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

    # open device connection
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

    # retreive data from device
    facts = {}

    NAPALM_GETTERS = [getter for getter in dir(network_driver) if getter.startswith("get_")]

    for getter in filter_list:
        getter_function = "get_{}".format(getter)
        if getter_function not in NAPALM_GETTERS:
            module.fail_json(msg="filter not recognized: " + getter)

        try:
            get_func = getattr(device, getter_function)
            result = get_func(**args.get(getter, {}))
            facts[getter] = result
        except NotImplementedError:
            if ignore_notimplemented:
                implementation_errors.append(getter)
            else:
                module.fail_json(
                    msg="The filter {} is not supported in napalm-{} [get_{}()]".format(
                        getter, dev_os, getter))
        except Exception as e:
            module.fail_json(msg="[{}] cannot retrieve device data: ".format(getter) + str(e))

    # close device connection
    try:
        device.close()
    except Exception as e:
        module.fail_json(msg="cannot close device connection: " + str(e))

    new_facts = {}
    # Prepend all facts with napalm_ for unique namespace
    for filter_name, filter_value in facts.items():
        # Make napalm get_facts to be directly accessible as variables
        if filter_name == "facts":
            for fact_name, fact_value in filter_value.items():
                napalm_fact_name = "napalm_" + fact_name
                new_facts[napalm_fact_name] = fact_value
        new_filter_name = "napalm_" + filter_name
        new_facts[new_filter_name] = filter_value
    results = {'ansible_facts': new_facts}

    if ignore_notimplemented:
        results['not_implemented'] = sorted(implementation_errors)

    module.exit_json(**results)


if __name__ == '__main__':
    main()
