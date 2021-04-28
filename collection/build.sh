ansible-galaxy collection build
mv napalm-napalm-0.9.12.tar.gz build/
# rm -r ~/.ansible/collections/ansible_collections/napalm
ansible-galaxy collection install build/napalm-napalm-0.9.12.tar.gz 
