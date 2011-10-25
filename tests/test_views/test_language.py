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

from . base import FunctionalTestsBase
import json


class LanguageHandlerFunctionalTests(FunctionalTestsBase):


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
