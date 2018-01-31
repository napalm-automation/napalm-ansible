from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.action.normal import ActionModule as _ActionModule


class ActionModule(_ActionModule):
    def run(self, tmp=None, task_vars=None):
        pc = self._play_context

        if hasattr(pc, "connection_user"):  # new in ansible 2.3
            # populate provider values with context values if not set
            provider = self._task.args.get('provider', {})

            provider['hostname'] = provider.get('hostname', provider.get('host', pc.remote_addr))
            provider['username'] = provider.get('username', pc.connection_user)
            provider['password'] = provider.get('password', pc.password)
            # Timeout can't be passed via command-line as Ansible defaults to a 10 second timeout
            provider['timeout'] = provider.get('timeout', 60)

            self._task.args['provider'] = provider

        result = super(ActionModule, self).run(tmp, task_vars)
        return result
