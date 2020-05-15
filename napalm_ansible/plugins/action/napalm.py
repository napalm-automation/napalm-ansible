from __future__ import absolute_import, division, print_function, unicode_literals

__metaclass__ = type

from ansible.plugins.action.normal import ActionModule as _ActionModule


class ActionModule(_ActionModule):
    def run(self, tmp=None, task_vars=None):
        pc = self._play_context

        if hasattr(pc, "connection_user"):
            # populate provider values with context values if not set
            provider = self._task.args.get("provider", {})

            provider["hostname"] = provider.get(
                "hostname", provider.get("host", pc.remote_addr)
            )
            username = provider.get("username", pc.connection_user)
            # Try to make ansible_connection=network_cli also work
            if not username:
                username = provider.get("username", pc.remote_user)
            provider["username"] = username
            provider["password"] = provider.get("password", pc.password)
            # Timeout can't be passed via command-line as Ansible defaults to a 10 second timeout
            provider["timeout"] = provider.get("timeout", 60)

            if hasattr(pc, "network_os"):
                provider["dev_os"] = provider.get("dev_os", pc.network_os)

            self._task.args["provider"] = provider

        result = super(ActionModule, self).run(tmp, task_vars)
        return result
