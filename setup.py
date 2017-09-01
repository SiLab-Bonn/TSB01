#!/usr/bin/env python
from setuptools import setup, find_packages  # This setup relies on setuptools since distutils is insufficient and badly hacked code

version = '0.0.1'
author = 'Christian Bespin'
author_email = 'bespin@physik.uni-bonn.de'

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='TSB01',
    version=version,
    description='DAQ for TSB01.',
    url='https://github.com/SiLab-Bonn/TSB01',
    license='MIT License',
    author=author,
    maintainer=author,
    author_email=author_email,
    maintainer_email=author_email,
    packages=find_packages(),
    setup_requires=['setuptools'],
    install_requires=required,
    include_package_data=True,  # accept all data files and directories matched by MANIFEST.in or found in source control
    package_data={'': ['README.*', 'VERSION'], 'docs': ['*'], 'examples': ['*']},
    keywords=['silicon', 'detector', 'xray'],
    platforms='any'
)
