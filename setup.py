#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Setup for Lauchpad."""

import io
from setuptools import setup, find_packages


INSTALL_REQUIRES = (
    ['fire>=0.2',
     'scikit-learn>=0.20',
     'importlib-resources==1.4.0',
     'numpy',
     'pandas',
     'tabulate',
     'pyyaml',
     'cachetools'
     ]
)


def version():
    return "1.1.2"


setup(
    name='launchpad',
    version=version(),
    description='A tool that automatically compile and launch slurm jobs \
                 based on a YAML configuration file.',
    long_description="",
    license='Expat License',
    author='Hao Sheng',
    author_email='haosheng@stanford.edu',
    url='https://github.com/stanfordmlgroup/LaunchPad',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='automation, sbatch',
    install_requires=INSTALL_REQUIRES,
    #packages=find_packages(),
    py_modules=['launchpad'],
    package_data={'launchpad': ['*.sh']},
    zip_safe=False,
    include_package_data=True,
    entry_points={'console_scripts': ['lp = launchpad:main'},
)
