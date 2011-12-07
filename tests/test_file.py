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
import pkg_resources
import shutil
from . import AybuCPFunctionalTestsBase


class MaxFilesException(Exception):
    pass


class OkException(Exception):
    pass


class FileHandlerFunctionalTests(AybuCPFunctionalTestsBase):

    def _get_test_file(self, name):
        return os.path.realpath(os.path.join(os.path.dirname(__file__),
                                             "data", name))

    def setUp(self):
        super(FileHandlerFunctionalTests, self).setUp()

        self.add_url = '/admin/files/add.html'
        self.remove_url = '/admin/files/delete.html'
        self.list_url = '/admin/files/list.html'
        self.index_url = '/admin/files/index.html'
        self.sample_image = self._get_test_file('sample.png')
        self.sample_file = self._get_test_file('data.txt')
        with open(self.sample_file, "wb") as f:
            f.write("123456\n")

        instance_module_name = 'aybu.instances.website_tests'
        self.app_upload_dir = os.path.join(
            pkg_resources.resource_filename(instance_module_name, 'public'),
            'uploads')

    def tearDown(self):
        shutil.rmtree(self.app_upload_dir)
        os.mkdir(self.app_upload_dir)
        super(FileHandlerFunctionalTests, self).tearDown()

    def test_create(self):
        # test missing params
        response = self.testapp.post(self.add_url, status=200)
        self.assertIn('success', response.json)
        self.assertIn('error', response.json)
        self.assertFalse(response.json['success'])

        # test missing name
        response = self.testapp.post(self.add_url,
                                     upload_files=[('file', self.sample_file)],
                                    status=200)
        self.assertFalse(response.json['success'])

        # test missing file
        response = self.testapp.post(self.add_url, params={'name': 'test.txt'},
                                    status=200)

        self.assertFalse(response.json['success'])


        # test ok
        response = self.testapp.post(self.add_url,
                                     params=dict(name='testfile.png'),
                                     upload_files=[('file', self.sample_file)],
                                    status=200)
        self.assertTrue(response.json['success'])
        self.assertIn('id', response.json)

        with self.assertRaises(OkException):
            # yeah, I know, it sucks.
            int(response.json['id'])
            raise OkException

        # test max image
        with self.assertRaises(MaxFilesException):
            for i in xrange(100):
                response = self.testapp.post(self.add_url,
                                             params=dict(name='testfile.png'),
                                             upload_files=[('file',
                                                            self.sample_image)],
                                            status=200)
                if not response.json['success']:
                    raise MaxFilesException()

    def test_delete(self):
        response = self.testapp.post(self.add_url,
                                     params=dict(name='testfile.png'),
                                     upload_files=[('file', self.sample_file)],
                                     status=200)

        self.assertIn('id', response.json)
        new_file_id = response.json['id']


        # test missing params
        response = self.testapp.post(self.remove_url, params=dict(), status=200)
        self.assertFalse(response.json['success'])
        self.assertIn('error', response.json)

        # test wrong id
        response = self.testapp.post(self.remove_url,
                                     params=dict(id=int(new_file_id) + 1),
                                     status=200)
        self.assertFalse(response.json['success'])
        self.assertIn('error', response.json)

        # test remove ok
        response = self.testapp.post(self.remove_url,
                                     params=dict(id=new_file_id), status=200)
        self.assertTrue(response.json['success'])
        self.assertIn('error', response.json)
        self.assertEqual(response.json['error'], {})

        # reassert error, file should not exist anymore
        response = self.testapp.post(self.remove_url,
                                     params=dict(id=new_file_id), status=200)
        self.assertFalse(response.json['success'])
        self.assertIn('error', response.json)

    def test_list(self):
        # assert file list is empty
        response = self.testapp.get(self.list_url, status=200)
        self.assertIn('datalen', response.json)
        self.assertIn('data', response.json)
        self.assertEqual(0, response.json['datalen'])
        self.assertEqual(0, len(response.json['data']))

        # add files and retest
        ids = []
        res = self.testapp.post(self.add_url,
                                params=dict(name='testfile.txt'),
                                upload_files=[('file', self.sample_file)],
                                status=200)
        ids.append(res.json['id'])

        res = self.testapp.post(self.add_url,
                                params=dict(name='testfile.txt'),
                                upload_files=[('file', self.sample_file)],
                                status=200)
        ids.append(res.json['id'])

        response = self.testapp.get(self.list_url, status=200)
        self.assertIn('datalen', response.json)
        self.assertIn('data', response.json)
        self.assertEqual(2, response.json['datalen'])
        self.assertEqual(2, len(response.json['data']))
        retr_ids = [i['id'] for i in response.json['data']]
        self.assertEqual(ids, retr_ids)

    def test_index(self):
        res = self.testapp.get(self.index_url, status=200)
        res2 = self.testapp.get(self.index_url + '?tiny=true', status=200)
        self.assertNotEqual(res.body, res2.body)
