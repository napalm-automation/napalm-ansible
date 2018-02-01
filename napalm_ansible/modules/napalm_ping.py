from ansible.module_utils.basic import AnsibleModule, return_values

"""
(c) 2017 Jason Edelman <jason@networktocode.com>

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
module: napalm_ping
author: "Jason Edelman (@jedelman8)"
version_added: "2.2"
short_description: "Executes ping on the device and returns response using NAPALM"
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
        choices: ['eos', 'junos', 'ios', 'vyos', 'ros']
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
    destination:
        description: Host or IP Address of the destination
        required: True
    source:
        description: Source address of echo request
        required: False
    ttl:
        description: Maximum number of hops
        required: False
    ping_timeout:
        description: Maximum seconds to wait after sending final packet
        required: False
    size:
        description: Size of request (bytes)
        required: False
    count:
        description: Number of ping request to send
        required: False
    vrf:
        description: vrf to source the echo request
        required: False

'''

EXAMPLES = '''
- napalm_ping:
    hostname: "{{ inventory_hostname }}"
    username: "napalm"
    password: "napalm"
    dev_os: "eos"
    destination: 10.0.0.5
    vrf: MANAGEMENT
    count: 2

- napalm_ping:
    provider: "{{ napalm_provider }}"
    destination: 8.8.8.8
    count: 2
'''

RETURN = '''
changed:
    description: ALWAYS RETURNS FALSE
    returned: always
    type: bool
    sample: True

results:
    description: structure response data of ping
    returned: always
    type: dict
    # when echo request succeeds
    sample: '{"success": {"packet_loss": 0, "probes_sent": 2,
            "results": [{"ip_address": "10.0.0.5:", "rtt": 1.71},
             {"ip_address": "10.0.0.5:", "rtt": 0.733}],
             "rtt_avg": 1.225, "rtt_max": 1.718, "rtt_min": 0.733,
             "rtt_stddev": 0.493}}'

alt_results:
    description: Example results key on failure
    returned: always
    type: dict
    # when echo request succeeds
    sample: '{"error": "connect: Network is unreachable\n"}}'
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
    os_choices = ['eos', 'junos', 'ios', 'vyos', 'ros']
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(type='str', required=False, aliases=['host']),
            username=dict(type='str', required=False),
            password=dict(type='str', required=False, no_log=True),
            provider=dict(type='dict', required=False),
            timeout=dict(type='int', required=False, default=60),
            optional_args=dict(required=False, type='dict', default=None),
            dev_os=dict(type='str', required=False, choices=os_choices),
            destination=dict(type='str', required=True),
            source=dict(type='str', required=False),
            ttl=dict(type='str', required=False),
            ping_timeout=dict(type='str', required=False),
            size=dict(type='str', required=False),
            count=dict(type='str', required=False),
            vrf=dict(type='str', required=False),
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
    destination = module.params['destination']

    ping_optional_args = {}
    ping_args = ['source', 'ttl', 'ping_timeout', 'size', 'count', 'vrf']
    for param, pvalue in module.params.items():
        if param in ping_args and pvalue is not None:
            ping_optional_args[param] = pvalue
    if 'ping_timeout' in ping_optional_args:
        ping_optional_args['timeout'] = ping_optional_args['ping_timeout']
        ping_optional_args.pop('ping_timeout')

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

    ping_response = device.ping(destination, **ping_optional_args)

    try:
        device.close()
    except Exception as e:
        module.fail_json(msg="cannot close device connection: " + str(e))

    module.exit_json(changed=False, results=ping_response)


if __name__ == '__main__':
    main()
