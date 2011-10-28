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

    def json_get(self, url, status):
        return self.testapp.get(url, status=status).json

    def base_assert(self, data):
        self.assertIn('success', data)
        self.assertIn('message', data)
        self.assertIn('metaData', data)

    def success_assert(self, data):
        self.base_assert(data)
        self.assertEqual(data['success'], True)

    def test_list_setting(self):

        response = self.json_get(url='/admin/settings/list', status=200)
        self.success_assert(response)
        self.assertEqual(len(response['dataset']), response['dataset_len'])

        # Save the length of dataset when no variables specified:
        # it is needed to jump forward/backward in the collection.
        # Example scenario: ExtJS paginator widget.
        collection_length = response['dataset_len']

        response = self.json_get('/admin/settings/list?start=0&limit=1',
                                 status=200)
        self.success_assert(response)
        self.assertEqual(response['dataset_len'], collection_length)
        self.assertEqual(len(response['dataset']), 1)

        response = self.json_get('/admin/settings/list?sort=name&dir=desc',
                                 status=200)
        self.success_assert(response)
        self.assertEqual(response['dataset_len'], collection_length)
        self.assertEqual(len(response['dataset']), collection_length)
