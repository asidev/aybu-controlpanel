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
import logging

log = logging.getLogger(__name__)


class SettingHandlerFunctionalTests(FunctionalTestsBase):

    def test_list_setting(self):
        response = self.testapp.get('/admin/settings/list', status=200)
        response = response.json
        dataset_len = len(response['dataset'])
        self.failUnless('success' in response)
        self.failUnless('metaData' in response)
        self.failUnless(response['success'] == True)
        self.assertEqual(dataset_len, response['dataset_len'])

        response = self.testapp.get('/admin/settings/list?start=0&limit=1',
                                    status=200)
        response = response.json
        self.failUnless('success' in response)
        self.failUnless('metaData' in response)
        self.assertEqual(response['success'], True)
        self.assertEqual(response['dataset_len'], dataset_len)
        self.assertEqual(len(response['dataset']), 1)

        response = self.testapp.get('/admin/settings/list?sort=name&dir=desc',
                                    status=200)
        response = response.json
        self.failUnless('success' in response)
        self.failUnless('metaData' in response)
        self.assertEqual(response['success'], True)
        self.assertEqual(response['dataset_len'], dataset_len)
        log.debug(response)
        self.assertEqual(len(response['dataset']), response['dataset_len'])
