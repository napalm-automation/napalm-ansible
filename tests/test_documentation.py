import json
import os
import pytest
import yaml
from glob import glob
from importlib import import_module

module_files = glob("napalm_ansible/modules/napalm_*.py")
modules = [module.split(".")[0].replace("/", ".") for module in module_files]


@pytest.fixture(params=modules)
def ansible_module(request):
    return request.param


def test_module_documentation_exists(ansible_module):
    module = import_module(ansible_module)
    content = dir(module)
    assert "DOCUMENTATION" in content
    assert "EXAMPLES" in content
    assert "RETURN" in content


def test_module_documentation_format(ansible_module):
    module = import_module(ansible_module)
    docs = yaml.safe_load(module.DOCUMENTATION)
    assert "author" in docs.keys()
    assert "description" in docs.keys()
    assert "short_description" in docs.keys()
    assert "options" in docs.keys()
    for param in docs["options"]:
        assert "description" in docs["options"][param].keys()
        assert "required" in docs["options"][param].keys()


def test_module_examples_format(ansible_module):
    module = import_module(ansible_module)
    module_name = ansible_module.replace("napalm_ansible.", "")
    examples = yaml.safe_load(module.EXAMPLES)
    params = yaml.safe_load(module.DOCUMENTATION)["options"].keys()
    for example in examples:
        if module_name in example.keys():
            for param in example[module_name]:
                assert param in params


def test_module_return_format(ansible_module):
    module = import_module(ansible_module)
    yaml.safe_load(module.RETURN)


def test_build_docs(ansible_module):
    try:
        os.mkdir("module_docs")
    except Exception:
        pass

    module = import_module(ansible_module)
    content = {}
    content["doc"] = yaml.safe_load(module.DOCUMENTATION)
    content["examples"] = module.EXAMPLES
    content["example_lines"] = module.EXAMPLES.split("\n")
    content["return_values"] = yaml.safe_load(module.RETURN)
    module_name = ansible_module.replace("napalm_ansible.", "").split(".")[-1]

    with open("module_docs/{0}.json".format(module_name), "w") as f:
        json.dump(content, f, indent=4, sort_keys=False)
