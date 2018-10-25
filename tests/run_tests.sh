#!/bin/sh
set -e

ansible-playbook -i napalm_connection/hosts napalm_connection/connection_info_missing.yaml
ansible-playbook -i napalm_connection/hosts napalm_connection/connection_info_in_vars.yaml
ansible-playbook -i napalm_connection/hosts napalm_connection/connection_info_in_args.yaml -u vagrant
ansible-playbook -i napalm_connection/hosts napalm_connection/connection_ansible_network_os.yaml -u vagrant
ANSIBLE_REMOTE_USER=vagrant ansible-playbook -i napalm_connection/hosts napalm_connection/connection_info_in_env.yaml 

ansible-playbook -i napalm_install_config/hosts -l "*.dry_run.*" napalm_install_config/config.yaml -C
ansible-playbook -i napalm_install_config/hosts -l "*.commit.*" napalm_install_config/config.yaml
ansible-playbook -i napalm_install_config/hosts -l "*.error*" napalm_install_config/config_error.yaml

ansible-playbook -i napalm_get_facts/hosts napalm_get_facts/get_facts_ok.yaml -l multiple_facts.ok
ansible-playbook -i napalm_get_facts/hosts napalm_get_facts/get_facts_not_implemented.yaml -l multiple_facts.not_implemented -e "ignore_notimplemented=true"
ansible-playbook -i napalm_get_facts/hosts napalm_get_facts/get_facts_not_implemented.yaml -l multiple_facts.not_implemented -e "ignore_notimplemented=false"
ansible-playbook -i napalm_get_facts/hosts napalm_get_facts/get_facts_error.yaml -l multiple_facts.error

ansible-playbook -i napalm_cli/hosts -l multiple_commands.ok napalm_cli/multiple_commands.yaml
ansible-playbook -i napalm_cli/hosts -l wrong_commands.err napalm_cli/wrong_args.yaml
ansible-playbook -i napalm_cli/hosts -l multiple_commands.ok napalm_cli/check_mode.yaml -C

echo "All tests successful!"
