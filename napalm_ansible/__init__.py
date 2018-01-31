import os
import ansible
from distutils.version import LooseVersion

message = """
To ensure Ansible can use the NAPALM modules you will have
to add the following configurtion to your Ansible configuration
file (ansible.cfg):

    [defaults]
    library = {path}/modules
    {action_plugins}

For more details on ansible's configuration file visit:
https://docs.ansible.com/ansible/latest/intro_configuration.html
"""


def main():
    path = os.path.dirname(__file__)
    if LooseVersion(ansible.__version__) < LooseVersion('2.3.0.0'):
        action_plugins = ""
    else:
        action_plugins = "action_plugins = {path}/plugins/action".format(path=path)

    print(message.format(path=path, action_plugins=action_plugins).strip())
