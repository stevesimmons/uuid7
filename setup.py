#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [ ]

test_requirements = ['pytest>=3', ]

setup(
    author="Stephen Simmons",
    author_email='mail@stevesimmons.com',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    description="UUID version 7, generating time-sorted UUIDs with 200ns time resolution and 48 bits of randomness",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='uuid7',
    name='uuid7',
    packages=find_packages(include=['uuid_extensions', 'uuid7.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/stevesimmons/uuid7',
    version='0.1.0',
    zip_safe=False,
)
