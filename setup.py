#!/usr/bin/env python
# coding: utf8

from setuptools import setup, find_packages

PREFIX = 'stubmaker'

with open('README.md') as f:
    readme = f.read()

setup(
    name='stubmaker',
    package_dir={PREFIX: 'src'},
    packages=[f'{PREFIX}.{package}' for package in find_packages('src')],
    py_modules=['make_stubs'],
    version='0.0.3',
    description='Tool for generating python stubs',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Vladimir Losev',
    author_email='losev@yandex-team.ru',
    python_requires='>=3.7.4',
    install_requires=[
        'docstring-parser',
        'typing_inspect',
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'stubmaker = make_stubs:main',
        ],
    },
    project_urls={'Source': 'https://github.com/Toloka/stubmaker'},
)
