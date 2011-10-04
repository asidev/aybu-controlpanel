import os

from setuptools import setup, find_packages

name = 'aybu-controlpanel'
version = '0.1a1'
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
requires = ['aybu-core', 'pyramid<1.3a', 'SQLAlchemy<0.8a', 'Babel',
            'aybu-website', "PyEnchant>=1.6.3", "BeautifulSoup"]
test_suite = 'tests'

entry_points = """\
[paste.app_factory]
    main = aybu.controlpanel:main
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
      zip_safe=zip_safe, install_requires=requires, tests_require=requires,
      test_suite=test_suite, entry_points=entry_points,
      message_extractors=message_extractors,
      paster_plugins=paster_plugins, namespace_packages=namespace_packages)
