import os
import ansible
from distutils.version import LooseVersion

message = """
To make sure ansible can make use of the napalm modules you will have
to add the following configurtion to your ansible configureation
file, i.e. `./ansible.cfg`:

    [defaults]
    library = {path}
    {action_plugins}

For more details on ansible's configuration file visit:
https://docs.ansible.com/ansible/latest/intro_configuration.html
"""

message_plugins = "action_plugins = {action_path}"


def main():
    path = os.path.dirname(__file__)
    if LooseVersion(ansible.__version__) < LooseVersion('2.3.0.0'):
        action_plugins = ""
    else:
        action_path = os.path.abspath(os.path.join(path, '..', 'action_plugins'))
        action_plugins = message_plugins.format(action_path=action_path)

    print(message.format(path=path, action_plugins=action_plugins).strip())
