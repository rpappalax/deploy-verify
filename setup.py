#!/usr/bin/env python

import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

REQUIREMENTS = [
    'requests>=2.7.0',
    'six>=1.9.0',
    'Fabric>=1.10.1',
    'boto>=2.38.0',
    'psutil==3.0.1',
    'tox>=1.9.0',
    'flake8>=2.4.0',
]

setup(
    name='deploy-verify',
    version='0.0.1',
    description='deploy-verify',
    long_description=README,
    author='Richard Pappalardo',
    author_email='rpappalax@gmail.com',
    url='https://github.com/rpappalax/deploy-verify',
    license="Apache License (2.0)",
    install_requires=REQUIREMENTS,
    keywords=['deployment', 'verification'],
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: Apache Software License',
    ],
    entry_points={
        'console_scripts': [
            'ticket = deploy_verify.main:ticket',
            'stack-check = deploy_verify.main:stack_check',
            'url-check = deploy_verify.main:url_check',
            'e2e = deploy_verify.main:e2e_test',
            'loadtest = deploy_verify.main:loadtest',
        ]
    },
)
