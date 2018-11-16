"""Setup file"""

import re
import ast
from setuptools import setup, find_packages

_VERSION_RE = re.compile(r'__version__\s+=\s+(.*)')

EXCLUDE_FROM_PACKAGES = ()

with open('rzdocs/__init__.py', 'rb') as f:
    VERSION = str(ast.literal_eval(_VERSION_RE.search(
        f.read().decode('utf-8')).group(1)))


setup(
    name='rzdocs',
    author='Roanuz',
    author_email='contact@roanuz.com',
    version=VERSION,
    url='http://github.com/roanuz/rzdocs',
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    include_package_data=True,
    install_requires=[
        'markdown',
        'markdown-include',
        'pyyaml',
        'dataclasses',
        'flask',
        'Click'
    ],
    py_modules=['rzdocs'],
    entry_points='''
        [console_scripts]
        rzdocs=rzdocs:app
    ''',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ]
)
