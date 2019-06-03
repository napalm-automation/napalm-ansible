"""setup.py file."""
from setuptools import setup, find_packages

with open("requirements.txt", "r") as fs:
    reqs = [r for r in fs.read().splitlines() if (len(r) > 0 and not r.startswith("#"))]

setup(
    name="napalm-ansible",
    version='1.0.0',
    packages=find_packages(exclude=("test*", "library")),
    author="David Barroso, Kirk Byers, Mircea Ulinic",
    author_email="dbarrosop@dravetech.com, ktbyers@twb-tech.com",
    description="Network Automation and Programmability Abstraction Layer with Multivendor support",
    classifiers=[
        'Topic :: Utilities',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
    ],
    url="https://github.com/napalm-automation/napalm-ansible",
    include_package_data=True,
    install_requires=reqs,
    entry_points={
        'console_scripts': [
            'napalm-ansible=napalm_ansible:main',
        ],
    }
)
