#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright 2010 Asidev s.r.l.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import os

from setuptools import setup, find_packages

name = 'aybu-controlpanel'
version = ':versiontools:aybu.controlpanel:'
description = 'aybu-controlpanel'

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
long_description = README + '\n\n' + CHANGES

classifiers = ["Programming Language :: Python",
               "Framework :: Pyramid", "Topic :: Internet :: WWW/HTTP",
               "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"]

author = ''
author_email = ''
url = ''
keywords = ''

include_package_data = True
zip_safe = False
requires = ('aybu-core', 'pyramid<1.3a', 'pyramid_handlers',
            'SQLAlchemy<0.8a', 'Babel', "PyEnchant>=1.6.3",
            'alembic', 'pyramid_beaker', 'aybu-website', )
setup_requires = ('versiontools >= 1.8',)
tests_require = ('nose', 'coverage', 'webtest')
test_suite = 'tests'

entry_points = """\
[paste.app_factory]
    main = aybu.controlpanel:main
[paste.paster_command]
    aybu-setup = aybu.core.utils.command:SetupApp
    uwsgi = pasteuwsgi.serve:ServeCommand
[nose.plugins.0.10]
    aybuconfig = aybu.core.testing:ReadAybuConfigPlugin
"""

paster_plugins = ['pyramid']
namespace_packages = ['aybu']
message_extractors = {
    '.': [
        ('**.py',   'lingua_python', None ),
    ]
}

setup(name=name, version=version, description=description,
      long_description=long_description, classifiers=classifiers,
      author=author, author_email=author_email, url=url, keywords=keywords,
      packages=find_packages(), include_package_data=include_package_data,
      zip_safe=zip_safe, install_requires=requires, tests_require=tests_require,
      test_suite=test_suite, entry_points=entry_points,
      setup_requires=setup_requires,
      message_extractors=message_extractors,
      paster_plugins=paster_plugins, namespace_packages=namespace_packages)
