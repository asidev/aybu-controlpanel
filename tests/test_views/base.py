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
from aybu.core.models import Base, add_default_data, User, Group
from webtest import TestApp
from paste.deploy.loadwsgi import appconfig
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker, Session
import json
import logging
import os.path
import pkg_resources
import unittest


class FunctionalTestsBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.log = logging.getLogger(cls.__name__)
        config = os.path.realpath(os.path.join(os.path.dirname(__file__),
                                               '..', '..', 'tests.ini'))
        cls.config = appconfig('config:{}#aybu-controlpanel'.format(config))
        cls.engine = engine_from_config(cls.config, prefix='sqlalchemy.')

    def populate(self):
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
        SessionF = sessionmaker(bind=self.engine)
        session = SessionF()
        source_ = pkg_resources.resource_stream('aybu.core.data',
                                                'default_data.json')
        data = json.loads(source_.read())
        source_.close()
        add_default_data(session, data)
        user = User(username=self.config['default_user.username'],
                    password=self.config['default_user.password'])
        session.merge(user)
        group = Group(name=u'admin')
        group.users.append(user)
        session.merge(group)
        session.commit()
        session.close()
        SessionF.close_all()

    def setUp(self):
        self.populate()
        app = main({}, **self.config)
        self.testapp = TestApp(app)
        self.login()

    def login(self):
        params = dict(submit='yes',
                      username=self.config['default_user.username'],
                      password=self.config['default_user.password'])
        response = self.testapp.post('/admin/login.html',
                                     params)
        response = response.follow(status=200)

    def tearDown(self):
        Session.close_all()
