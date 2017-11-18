import json
import os
import pytest
import yaml
from glob import glob
from importlib import import_module

module_files = glob('napalm_ansible/napalm_*.py')
modules = [module.split('.')[0].replace('/', '.') for module in module_files]


@pytest.fixture(params=modules)
def ansible_module(request):
    return request.param


def test_module_documentation_exists(ansible_module):
    module = import_module(ansible_module)
    content = dir(module)
    assert 'DOCUMENTATION' in content
    assert 'EXAMPLES' in content
    assert 'RETURN' in content


def test_module_documentation_format(ansible_module):
    module = import_module(ansible_module)
    docs = yaml.load(module.DOCUMENTATION)
    assert 'author' in docs.keys()
    assert 'description' in docs.keys()
    assert 'short_description' in docs.keys()
    assert 'options' in docs.keys()
    for param in docs['options']:
        assert 'description' in docs['options'][param].keys()
        assert 'required' in docs['options'][param].keys()


def test_module_examples_format(ansible_module):
    module = import_module(ansible_module)
    yaml.load(module.EXAMPLES)


def test_module_return_format(ansible_module):
    module = import_module(ansible_module)
    yaml.load(module.RETURN)


def test_build_docs(ansible_module):
    try:
        os.mkdir('module_docs')
    except Exception:
        pass

    module = import_module(ansible_module)
    content = {}
    content['doc'] = yaml.load(module.DOCUMENTATION)
    content['examples'] = yaml.load(module.EXAMPLES)
    content['return'] = yaml.load(module.RETURN)
    module = ansible_module.replace('napalm_ansible.', '')
    with open('module_docs/{0}.json'.format(module), 'w') as f:
        json.dump(content, f, indent=4, sort_keys=True)
