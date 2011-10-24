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

from aybu.controlpanel import main
from aybu.core.models import populate
from pyramid import testing
from webtest import TestApp
import ConfigParser
import json
import logging
import os.path
import unittest

log = logging.getLogger(__name__)


class LanguageHandlerFunctionalTests(unittest.TestCase):

    def setUp(self):

        # Step 1: open & read config file.
        parser = ConfigParser.ConfigParser()
        config = os.path.realpath(os.path.join(os.path.dirname(__file__),
                                               '..', '..', 'tests.ini'))

        try:
            with open(config) as f:
                parser.readfp(f)

        except IOError:
            raise Exception("Cannot find configuration file '%s'" % config)

        # Section of INI file from which read settings.
        section = 'app:aybu-controlpanel'

        # Step 2: load default data
        default_data = parser.get(section, 'default_data')
        databag = os.path.realpath(os.path.join(os.path.dirname(config),
                                                os.path.dirname(default_data),
                                                os.path.basename(default_data)))
        try:
            with open(databag) as f:
                data = json.loads(f.read())

        except IOError:
            raise Exception("Cannot find data file '%s'" % databag)

        populate(parser, data, section)

        settings = {opt: parser.get(section, opt)
                    for opt in parser.options(section)}
        app = main({}, **settings)
        self.testapp = TestApp(app)

    def test_enable_disable_language(self):

        resource = self.testapp.get('/admin/language/enable.html', status=200)
        response = json.loads(resource.body)
        self.failUnless('success' in response)
        self.failUnless('msg' in response)
        self.failUnless(response['success'] is False)

        url = '/admin/language/enable.html?lang_id=2'
        resource = self.testapp.get(url, status=200)
        response = json.loads(resource.body)
        self.failUnless(response['success'] is False)

        url = '/admin/language/enable.html?src_clone_language_id=1'
        resource = self.testapp.get(url, status=200)
        response = json.loads(resource.body)
        self.failUnless(response['success'] is False)

        url = '/admin/language/enable.html?lang_id=2&src_clone_language_id=1'
        resource = self.testapp.get(url, status=200)
        response = json.loads(resource.body)
        self.failUnless(response['success'] is False) # max_languages reached!

        resource = self.testapp.get('/admin/language/disable.html', status=200)
        response = json.loads(resource.body)
        self.failUnless('success' in response)
        self.failUnless('msg' in response)
        self.failUnless(response['success'] is False)

        url = '/admin/language/disable.html?lang_id=2'
        resource = self.testapp.get(url, status=200)
        response = json.loads(resource.body)
        self.failUnless('success' in response)
        self.failUnless('msg' in response)
        self.failUnless(response['success'] is True)

        url = '/admin/language/enable.html?lang_id=2&src_clone_language_id=1'
        resource = self.testapp.get(url, status=200)
        response = json.loads(resource.body)
        self.failUnless(response['success'] is True)

        url = '/admin/language/disable.html?lang_id=3'
        resource = self.testapp.get(url, status=200)
        response = json.loads(resource.body)
        self.failUnless('success' in response)
        self.failUnless('msg' in response)
        self.failUnless(response['success'] is True)

        url = '/admin/language/disable.html?lang_id=2'
        resource = self.testapp.get(url, status=200)
        response = json.loads(resource.body)
        self.failUnless('success' in response)
        self.failUnless('msg' in response)
        self.failUnless(response['success'] is True)

        url = '/admin/language/disable.html?lang_id=1'
        resource = self.testapp.get(url, status=200)
        response = json.loads(resource.body)
        self.failUnless('success' in response)
        self.failUnless('msg' in response)
        self.failUnless(response['success'] is False) #Last enabled language.
