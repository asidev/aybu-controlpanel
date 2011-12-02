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
from aybu.core.models import (populate,
                              engine_from_config_parser,
                              create_session)
from webtest import TestApp
from sqlalchemy.orm import Session
import ConfigParser
import json
import logging
import os.path
import unittest


class FunctionalTestsBase(unittest.TestCase):

    def setUp(self):

        self.log = logging.getLogger(self.__class__.__name__)
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
        self.username = parser.get(section, 'default_user.username')
        self.password = parser.get(section, 'default_user.password')
        databag = os.path.realpath(os.path.join(os.path.dirname(config),
                                                os.path.dirname(default_data),
                                                os.path.basename(default_data)))
        self.engine = engine_from_config_parser(parser, section)
        session = create_session(self.engine)()

        try:
            with open(databag) as f:
                data = json.loads(f.read())

        except IOError:
            raise Exception("Cannot find data file '%s'" % databag)

        else:
            populate(parser, data, session)
            session.close()


        # Step 5: create webapp
        settings = {opt: parser.get(section, opt)
                    for opt in parser.options(section)}
        app = main({}, **settings)
        self.testapp = TestApp(app)
        self.login()

    def login(self):
        params = dict(submit='yes',
                      username=self.username,
                      password=self.password)
        response = self.testapp.post('/admin/login.html',
                                     params)
        response = response.follow(status=200)

    def tearDown(self):
        Session.close_all()
