import os

message = """
To make sure ansible can make use of the napalm modules you will have
to add the following configurtion to your ansible configureation
file, i.e. `./ansible.cfg`:

    [defaults]
    library = {path}

For more details on ansible's configuration file visit:
https://docs.ansible.com/ansible/latest/intro_configuration.html
"""


def main():
    path = os.path.dirname(__file__)
    print(message.format(path=path).strip())
