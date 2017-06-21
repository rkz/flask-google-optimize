# -*- coding: utf-8 -*-

"""
Flask-Google-Optimize
---------------------

Run server-side experiments in Google Optimize within your Flask app.
"""

import ast
import os
import re
from setuptools import setup


# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# Extract version from source code
_version_re = re.compile(r'__version__\s+=\s+(.*)')
with open('flask_google_optimize.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(f.read().decode('utf-8')).group(1)))

setup(
    name='Flask-Google-Optimize',
    version=version,
    author=u'Raphaël Kolm',
    author_dev='raphael@privateaser.com',
    long_description=__doc__,
    py_modules=['flask_google_optimize'],
    install_requires=[
        'Flask'
    ]
)
