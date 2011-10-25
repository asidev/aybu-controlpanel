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
from . base import FunctionalTestsBase

class MaxImagesException(Exception):
    pass

class OkException(Exception):
    pass


class ImageHandlerFunctionalTests(FunctionalTestsBase):

    def _get_test_file(self, name):
        return os.path.realpath(os.path.join(os.path.dirname(__file__),
                                             "data", name))

    def setUp(self):
        super(ImageHandlerFunctionalTests, self).setUp()

        self.add_url = '/admin/images/add.html'
        self.update_url = '/admin/images/update.html'
        self.sample_image = self._get_test_file('sample.png')

        instance_module_name = 'aybu.instances.website_tests'
        self.app_upload_dir = os.path.join(
            pkg_resources.resource_filename(instance_module_name, 'public'),
            'uploads')

    def tearDown(self):
        shutil.rmtree(self.app_upload_dir)
        os.mkdir(self.app_upload_dir)
        super(ImageHandlerFunctionalTests, self).tearDown()

    def test_create(self):
        # test missing params
        response = self.testapp.post(self.add_url)
        self.assertIn('success', response.json)
        self.assertIn('error', response.json)
        self.assertFalse(response.json['success'])

        # test missing name
        response = self.testapp.post(self.add_url,
                                     upload_files=[('file', self.sample_image)])
        self.assertFalse(response.json['success'])

        # test missing file extension
        response = self.testapp.post(self.add_url,
                                     params=dict(name='testfile'),
                                     upload_files=[('file', self.sample_image)])
        self.assertFalse(response.json['success'])

        # test wrong file type
        response = self.testapp.post(self.add_url,
                                     params=dict(name='testfile.png'),
                                     upload_files=[('file', "sample.png",
                                                    "123456")])
        self.assertFalse(response.json['success'])

        # test ok
        response = self.testapp.post(self.add_url,
                                     params=dict(name='testfile.png'),
                                     upload_files=[('file', self.sample_image)])
        self.assertTrue(response.json['success'])
        self.assertIn('id', response.json)

        with self.assertRaises(OkException):
            # yeah, I know, it sucks.
            int(response.json['id'])
            raise OkException

        # test max image
        with self.assertRaises(MaxImagesException):
            for i in xrange(100):
                response = self.testapp.post(self.add_url,
                                             params=dict(name='testfile.png'),
                                             upload_files=[('file', self.sample_image)])
                if not response.json['success']:
                    raise MaxImagesException()


    def test_update(self):
        response = self.testapp.post(self.add_url,
                                     params=dict(name='testfile.png'),
                                     upload_files=[('file', self.sample_image)])
        new_image_id = response.json['id']


        # test missing id_
        response = self.testapp.post(self.update_url, params={})
        self.assertFalse(response.json['success'])
        self.assertIn('errors', response.json)
        self.assertIn('id', response.json['errors'])

        # test not found
        wrong_id = int(new_image_id) + 1
        response = self.testapp.post(self.update_url, params={'id': wrong_id})
        self.assertFalse(response.json['success'])
        self.assertIn('errors', response.json)
        self.assertIn('id', response.json['errors'])

        # test no params
        response = self.testapp.post(self.update_url, params={'id': new_image_id})
        self.assertFalse(response.json['success'])
        self.assertIn('errors', response.json)
        self.assertIn('name', response.json['errors'])
        self.assertIn('file', response.json['errors'])

        # test wrong name
        response = self.testapp.post(self.update_url,
                                    params={'id': new_image_id,
                                            'name': ''})
        self.assertFalse(response.json['success'])
        self.assertIn('errors', response.json)
        self.assertIn('name', response.json['errors'])


        # test update name ok
        response = self.testapp.post(self.update_url,
                                     params={'id': new_image_id, 'name':
                                             'nuovonome.png'})
        self.assertTrue(response.json['success'])
        self.assertNotIn('errors', response.json)

        # test update file ok
        response = self.testapp.post(self.update_url,
                                     params={'id': new_image_id},
                                     upload_files=[('file', self.sample_image)])
        self.assertTrue(response.json['success'])
        self.assertNotIn('errors', response.json)


