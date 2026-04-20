"""
(c) 2020 Kirk Byers <ktbyers@twb-tech.com>
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
from __future__ import unicode_literals, print_function
import os.path
from ansible.module_utils.basic import AnsibleModule


# FIX for Ansible 2.8 moving this function and making it private
# greatly simplified for napalm-ansible's use
def return_values(obj):
    """ Return native stringified values from datastructures.

    For use with removing sensitive values pre-jsonification."""
    yield str(obj)


DOCUMENTATION = """
---
module: napalm_get_config
author: "Anirudh Kamath (@anirudhkamath)"
version_added: "2.9"
short_description: "Gathers configuration from a network device via napalm"
description:
    - "Gathers configuration from a network device via the Python module napalm"
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
    retrieve:
        description:
            - Which configuration type you want to populate, default is all of them.
        required: False
    full:
        description:
            - Retrieve all the configuration. For instance, on ios, "sh run all".
        required: False
    sanitized:
        description:
            - Remove secret data
        required: False
"""

EXAMPLES = """
- name: Collect device configuration object using NAPALM
  napalm_get_config:
    hostname: "{{ inventory_hostname }}"
    username: "{{ user }}"
    password: "{{ password }}"
    dev_os: "os"
  register: config_result

- name: Write running config to backup file
  copy:
    content: "{{ config_result.napalm_config.running }}"
    dest: "{{ file }}"
"""

RETURN = """
napalm_config:
    description: "The object returned is a dictionary with a key for each configuration store:
        - running
        - candidate
        - startup
    returned: always
    type: dict
    sample: "{
        "running": "",
        "startup": "",
        "candidate": "",
    }"
"""

napalm_found = False
try:
    from napalm import get_network_driver
    from napalm.base import ModuleImportError

    napalm_found = True
except ImportError:
    pass


def main():
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(type="str", required=False, aliases=["host"]),
            username=dict(type="str", required=False),
            password=dict(type="str", required=False, no_log=True),
            provider=dict(type="dict", required=False),
            timeout=dict(type="int", required=False, default=60),
            optional_args=dict(required=False, type="dict", default=None),
            dev_os=dict(type="str", required=False),
            retrieve=dict(type="str", required=False, default=None),
            full=dict(type="str", required=False, default=None),
            sanitized=dict(type="str", required=False, default=None),
        ),
    )

    if not napalm_found:
        module.fail_json(msg="the python module napalm is required")

    provider = module.params["provider"] or {}

    no_log = ["password", "secret"]
    for param in no_log:
        if provider.get(param):
            module.no_log_values.update(return_values(provider[param]))
        if provider.get("optional_args") and provider["optional_args"].get(param):
            module.no_log_values.update(
                return_values(provider["optional_args"].get(param))
            )
        if module.params.get("optional_args") and module.params["optional_args"].get(
            param
        ):
            module.no_log_values.update(
                return_values(module.params["optional_args"].get(param))
            )

    # allow host or hostname
    provider["hostname"] = provider.get("hostname", None) or provider.get("host", None)
    # allow local params to override provider
    for param, pvalue in provider.items():
        if module.params.get(param) is not False:
            module.params[param] = module.params.get(param) or pvalue

    hostname = module.params["hostname"]
    username = module.params["username"]
    dev_os = module.params["dev_os"]
    password = module.params["password"]
    timeout = module.params["timeout"]
    retrieve = module.params["retrieve"]
    full = module.params["full"]
    sanitized = module.params["sanitized"]

    argument_check = {"hostname": hostname, "username": username, "dev_os": dev_os}
    for key, val in argument_check.items():
        if val is None:
            module.fail_json(msg=str(key) + " is required")

    if module.params["optional_args"] is None:
        optional_args = {}
    else:
        optional_args = module.params["optional_args"]

    try:
        network_driver = get_network_driver(dev_os)
    except ModuleImportError as e:
        module.fail_json(msg="Failed to import napalm driver: " + str(e))

    try:
        device = network_driver(
            hostname=hostname,
            username=username,
            password=password,
            timeout=timeout,
            optional_args=optional_args,
        )
        device.open()
    except Exception as e:
        module.fail_json(msg="cannot connect to device: " + str(e))

    try:
        get_config_kwargs = {} # kwargs should match driver specific `get_config` method specs
        if retrieve is not None:
            get_config_kwargs["retrieve"] = retrieve
        if full is not None:
            get_config_kwargs["full"] = full
        if sanitized is not None:
            get_config_kwargs["sanitized"] = sanitized
        config_dict = device.get_config(**get_config_kwargs)
        results = {
            "changed": False,
            "napalm_config": config_dict,
        }
    except Exception as e:
        module.fail_json(msg="cannot retrieve device config:" + str(e))

    module.exit_json(**results)


if __name__ == "__main__":
    main()
