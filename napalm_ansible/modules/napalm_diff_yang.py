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
from ansible.module_utils.basic import AnsibleModule

try:
    import napalm_yang
except ImportError:
    napalm_yang = None


DOCUMENTATION = '''
---
module: napalm_diff_yang
author: "David Barroso (@dbarrosop)"
version_added: "0.0"
short_description: "Return diff of two YANG objects"
description:
    - "Create two YANG objects from dictionaries and runs mehtod"
    - "napalm_yang.utils.diff on them."
requirements:
    - napalm-yang
options:
    models:
        description:
          - List of models to parse
        required: True
    first:
        description:
          - Dictionary with the data to load into the first YANG object
        required: True
    second:
        description:
          - Dictionary with the data to load into the second YANG object
        required: True
'''

EXAMPLES = '''
- napalm_diff_yang:
    first: "{{ candidate.yang_model }}"
    second: "{{ running_config.yang_model }}"
    models:
     - models.openconfig_interfaces
  register: diff
'''

RETURN = '''
diff:
    description: "Same output as the method napalm_yang.utils.diff"
    returned: always
    type: dict
    sample: '{
            "interfaces": {
                "interface": {
                    "both": {
                        "Port-Channel1": {
                            "config": {
                                "description": {
                                    "first": "blah",
                                    "second": "Asadasd"
                                }
                            }
                        }
                    }
                }
            }'
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
            first=dict(type='dict', required=True),
            second=dict(type='dict', required=True),
        ),
        supports_check_mode=True
    )

    if not napalm_yang:
        module.fail_json(msg="the python module napalm-yang is required")

    first = get_root_object(module.params["models"])
    first.load_dict(module.params["first"])

    second = get_root_object(module.params["models"])
    second.load_dict(module.params["second"])

    diff = napalm_yang.utils.diff(first, second)

    module.exit_json(yang_diff=diff)


if __name__ == '__main__':
    main()
