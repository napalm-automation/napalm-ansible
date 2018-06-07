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

import re
import os.path
import hashlib

from ansible.module_utils.basic import AnsibleModule, return_values

DOCUMENTATION = '''
---
module: napalm_get_config
author: "Dmitry Zykov (@dmitryzykov)"
version_added: "1.1"
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
            - File where to save retrieved configuration from a device.
        default: None
        required: False
    type:
        description:
            - Config type to retreive from device. If retrieved config is empty retrieve
              "running" type instead.
        default: running
        required: False
        choices: ['running', 'candidate', 'startup']
    strip_comments:
        description:
            - Strip comments with timestamps from the config to behave in idempotent way.
        default: False
        required: False
'''

EXAMPLES = '''
- name: get the running config with stripped comments
  napalm_get_config:
    hostname: "{{ inventory_hostname }}"
    username: "{{ username }}"
    dev_os: "{{ os }}"
    password: "{{ password }}"
    dest: "../backup/{{ inventory_hostname }}"
    type: running
    strip_comments: True

- name: get the startup config using provider
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

msg:
    description: retrieved config file
    returned: always
    type: string
    sample: "## Last commit: 2018-05-30 13:52:39 UTC by root ..."
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
    config_types = ['running', 'candidate', 'startup']

    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(type='str', required=False, aliases=['host']),
            username=dict(type='str', required=False),
            password=dict(type='str', required=False, no_log=True),
            provider=dict(type='dict', required=False),
            timeout=dict(type='int', required=False, default=60),
            optional_args=dict(required=False, type='dict', default=None),
            dev_os=dict(type='str', required=False),
            dest=dict(type='str', required=False, default=None),
            type=dict(type='str', required=False, choices=config_types, default="running"),
            strip_comments=dict(type='bool', required=False, default=False),
        ),
        supports_check_mode=True
    )

    changed = False

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
    strip_comments = module.params['strip_comments']

    argument_check = {'hostname': hostname, 'username': username, 'dev_os': dev_os}
    for key, val in argument_check.items():
        if val is None:
            module.fail_json(msg=str(key) + " is required")

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

        # strip comments from the config:
        # (?m) enables the multiline mode
        # ^ asserts that we are at the start
        # <space>*# matches the character # at the start with or without preceding spaces
        # .* matches all the following characters except line breaks
        # replacing those matched characters with empty string
        if strip_comments:
            if dev_os in ['junos']:
                # strip comments with leading #
                config = re.sub(r'(?m)^ *#.*\n?', '', config)
            elif dev_os in ['ios', 'iosxr', 'nxos', 'nxos_ssh', 'eos']:
                # strip comments with leading !
                config = re.sub(r'(?m)^ *!.*\n?', '', config)

        if dest:
            # check whether the config already exists
            if os.path.isfile(dest):
                config_checksum = hashlib.sha1(config).hexdigest()
                dest_checksum = module.sha1(dest)

                # if they are different, save the new version
                if dest_checksum != config_checksum:
                    save_to_file(config, dest)
                    changed = True
            else:
                save_to_file(config, dest)
                changed = True

    except Exception as e:
        module.fail_json(msg="cannot retrieve config:" + str(e))

    try:
        device.close()
    except Exception as e:
        module.fail_json(msg="cannot close device connection: " + str(e))

    module.exit_json(changed=changed, msg=config)


if __name__ == '__main__':
    main()
