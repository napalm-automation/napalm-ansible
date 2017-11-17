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


def test_module_documentation_format(ansible_module):
    module = import_module(ansible_module)
    yaml.load(module.DOCUMENTATION)


def test_module_examples_format(ansible_module):
    module = import_module(ansible_module)
    yaml.load(module.EXAMPLES)
