
DOCS = """
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
        choices: ['eos', 'junos', 'iosxr', 'fortios', 'ios', 'mock', 'nxos', 'nxos_ssh', 'panos',
        'vyos']
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
"""

os_choices = ['eos', 'junos', 'iosxr', 'fortios', 'ios', 'mock', 'nxos',
              'nxos_ssh', 'panos', 'vyos', 'ros']

napalm_args_spec = {
    'hostname': dict(type='str', required=False, aliases=['host']),
    'username': dict(type='str', required=False),
    'password': dict(type='str', required=False, no_log=True),
    'dev_os': dict(type='str', required=False, choices=os_choices),
    'provider': dict(type='dict', required=False),
    'timeout': dict(type='int', required=False, default=60),
    'optional_args': dict(required=False, type='dict', default=None)
}
