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


class StructuregHandlerFunctionalTests(FunctionalTestsBase):

    def json_get(self, url, status):
        return self.testapp.get(url, status=status).json

    def base_assert(self, data):
        self.assertIn('success', data)
        self.assertIn('message', data)
        self.assertIn('metaData', data)

    def success_assert(self, data):
        self.base_assert(data)
        self.assertEqual(data['success'], True)

    def test_tree(self):
        response = self.json_get(url='/admin/structure/tree.html', status=200)
        self.assertNotEqual(len(response), 0)

    def test_link_list(self):
        response = self.testapp.get(url='/admin/structure/link_list.html', 
                                    status=200)
        self.assertNotEqual(response, '')

    def test_list(self):
        response = self.json_get(url='/admin/structure/list.html', 
                                 status=200)
        self.success_assert(response)

    def test_info(self):
        response = self.json_get(url='/admin/structure/info.html', 
                                 status=400)
        self.base_assert(response)
        self.assertEqual(response['success'], False)

        response = self.json_get(url='/admin/structure/info.html?id=1',
                                 status=200)
        self.success_assert(response)

    def test_create(self):
        response = self.json_get(url='/admin/structure/create.html', 
                                 status=501)
        self.base_assert(response)
        self.assertEqual(response['success'], False)

        response = self.json_get(url='/admin/structure/create.html?type=Menu',
                                 status=501)
        self.base_assert(response)
        self.assertEqual(response['success'], False)

        response = self.json_get(url='/admin/structure/create.html?type=Section',
                                 status=500)
        self.base_assert(response)
        self.assertEqual(response['success'], False)

        url = '/admin/structure/create.html?type=Section&parent_id=1'
        response = self.json_get(url=url, status=500)
        self.base_assert(response)
        self.assertEqual(response['success'], False)

        url = '/admin/structure/create.html?type=Section&parent_id=1&button_label=Hi'
        response = self.json_get(url=url, status=200)
        self.success_assert(response)

        url = '/admin/structure/create.html?type=Page&parent_id=1&button_label=Hi&sitemap_priority=1&page_type_id=1'
        response = self.json_get(url=url, status=200)
        self.success_assert(response)
        url = '/admin/structure/info.html?id=%s' % response['dataset'][0]['id']
        response = self.json_get(url=url, status=200)
        self.success_assert(response)

        url = '/admin/structure/create.html?type=Section&parent_id=1'
        response = self.json_get(url=url, status=200)
