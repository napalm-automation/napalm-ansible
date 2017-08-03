"""setup.py file."""
import uuid

from setuptools import setup
from pip.req import parse_requirements


install_reqs = parse_requirements('requirements.txt', session=uuid.uuid1())
reqs = [str(ir.req) for ir in install_reqs]


setup(
    name="napalm-ansible",
    version='0.7.0',
    packages=["napalm_ansible"],
    author="David Barroso, Kirk Byers, Mircea Ulinic",
    author_email="dbarrosop@dravetech.com, ktbyers@twb-tech.com",
    description="Network Automation and Programmability Abstraction Layer with Multivendor support",
    classifiers=[
        'Topic :: Utilities',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
    ],
    url="https://github.com/napalm-automation/napalm-base",
    include_package_data=True,
    install_requires=reqs,
    entry_points={
        'console_scripts': [
            'napalm-ansible=napalm_ansible:main',
        ],
    }
)
