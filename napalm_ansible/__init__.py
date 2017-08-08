import os

message = """
To make sure ansible can make use of the napalm modules you will have
to add the following configurtion to your ansible configureation
file, i.e. `./ansible.cfg`:

    [defaults]
    library = {path}
    action_plugins = {action_path}

For more details on ansible's configuration file visit:
https://docs.ansible.com/ansible/latest/intro_configuration.html
"""


def main():
    path = os.path.dirname(__file__)
    action_path = os.path.join(path,  'action_plugins')
    print(message.format(path=path, action_path=action_path).strip())
