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

from pyramid import testing
import logging
try:
    import unittest2 as unittest
except:
    import unittest


log = logging.getLogger(__name__)


class NodeViewsTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    """
    def test_index(self):
        raise NotImplementedError()

    def test_create(self):
        raise NotImplementedError()

    def test_update(self):
        raise NotImplementedError()

    def test_delete(self):
        raise NotImplementedError()

    def test_search(self):
        raise NotImplementedError()

    """
