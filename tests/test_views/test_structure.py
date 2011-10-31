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

    def test_tree(self):
        response = self.json_get(url='/admin/structure/tree.html', status=200)
        self.assertNotEqual(len(response), 0)

    def test_link_list(self):
        response = self.testapp.get(url='/admin/structure/link_list.html', 
                                    status=200)
        self.assertNotEqual(response, '')
