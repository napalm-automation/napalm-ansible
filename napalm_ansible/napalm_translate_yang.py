#!/usr/bin/python
# -*- coding: utf-8 -*-

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
from ansible.module_utils.basic import AnsibleModule

try:
    import napalm_yang
except ImportError:
    napalm_yang = None


DOCUMENTATION = '''
---
module: napalm_translate_yang
author: "David Barroso (@dbarrosop)"
version_added: "0.0"
short_description: "Translate a YANG object to native configuration"
description:
    - "Load a YANG object from a dict and translates the object to native"
    - "configuration"
requirements:
    - napalm-yang
options:
    models:
        description:
          - List of models to parse
        required: True
    profiles:
        description:
          - List of profiles to use to translate the object
        required: True
    data:
        description:
          - dict to load into the YANG object
        required: True
    merge:
        description:
          - When translating config, merge resulting config here
        required: False
    replace:
        description:
          - When translating config, replace resulting config here
        required: False
'''

EXAMPLES = '''
- name: "Translate config"
  napalm_translate_yang:
    data: "{{ interfaces.yang_model }}"
    profiles: ["eos"]
    models:
        - models.openconfig_interfaces
  register: config
'''

RETURN = '''
config:
  description: "Native configuration"
  returned: always
  type: string
  sample: "interface Ethernet2\n no switchport\n ip address 192.168.0.1/24 \n"
'''


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


def main():
    module = AnsibleModule(
        argument_spec=dict(
            models=dict(type="list", required=True),
            profiles=dict(type="list", required=False),
            data=dict(type='dict', required=True),
            merge=dict(type='dict', required=False),
            replace=dict(type='dict', required=False),
        ),
        supports_check_mode=True
    )

    if not napalm_yang:
        module.fail_json(msg="the python module napalm-yang is required")

    root = get_root_object(module.params["models"])
    root.load_dict(module.params["data"])

    running = get_root_object(module.params["models"])
    args = {}

    if module.params["merge"]:
        args["merge"] = running
        running.load_dict(module.params["merge"])
    elif module.params["replace"]:
        args["replace"] = running
        running.load_dict(module.params["replace"])

    config = root.translate_config(profile=module.params["profiles"], **args)

    module.exit_json(config=config)


if __name__ == '__main__':
    main()
