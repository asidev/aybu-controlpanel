#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except:
    import unittest

from pyramid import testing
from logging import getLogger

from babel import Locale

from aybu.website.lib.database import fill_db
from aybu.website.models import Menu, Page, Section, InternalLink, ExternalLink
from aybu.website.models import Node, View, NodeInfo
from aybu.controlpanel.lib.structure import check_url_part, boolify
from aybu.controlpanel.lib.structure import is_valid_parent, create_node

import random

log = getLogger(__name__)


class ModelsTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

        from aybu.website.models.base import Base
        from sqlalchemy import create_engine
        from sqlalchemy.orm import scoped_session
        from sqlalchemy.orm import sessionmaker

        self.engine = create_engine('sqlite:///:memory:')
        self.session = scoped_session(sessionmaker())
        self.session.configure(bind=self.engine)

        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

        fill_db(self.session)

    def tearDown(self):
        self.session.remove()
        testing.tearDown()


class StructureTests(ModelsTests):

    def test_check_url_part(self):

        title = 'La nostra storia'

        correct_url_part = 'la_nostra_storia'

        for url_part in (title, None, title.upper(), correct_url_part):

            generated_url_part = check_url_part(url_part, title)

            # Check if the calculated url is equal to the expected result
            self.assertEqual(correct_url_part, generated_url_part)

            # Check no spaces are in result
            self.assertNotIn(' ', generated_url_part)

            # Check no capital letter in result
            pattern = "[A-Z]"
            self.assertNotRegexpMatches(generated_url_part, pattern)

        correct_url_part = 'storia'

        for url_part in ('storia  ', 'Storia'):

            generated_url_part = check_url_part(url_part, title)

            # Check if the calculated url is equal to the expected result
            self.assertEqual(correct_url_part, generated_url_part)

            # Check no spaces are in result
            self.assertNotIn(' ', generated_url_part)

            # Check no capital letter in result
            pattern = "[A-Z]"
            self.assertNotRegexpMatches(generated_url_part, pattern)

    def test_boolify(self):

        params = {}

        for enabled in ('on', 'ON', True, 'true', 'True', 'TRUE', 'yes', 'ok',
                        'y'):
            self.assertIs(boolify(enabled), True)

        for enabled in ('off', 'OFF', 'no', False, 'None', 'null', 'none', ''):
            self.assertIs(boolify(enabled), False)


    def test_is_valid_parent(self):

        for class_ in (Menu, Page, Section):
            rand = random.randrange(0, self.session.query(class_).count())
            row = self.session.query(class_)[rand]
            self.assertIs(is_valid_parent(row), True)

        for class_ in (InternalLink, ExternalLink):
            rand = random.randrange(0, self.session.query(class_).count())
            row = self.session.query(class_)[rand]
            self.assertIs(is_valid_parent(row), False)

        for instance in (dict(), list(), None, 1, True, False, ''):
            self.assertIs(is_valid_parent(instance), False)

    def test_create_node(self):

        nodes = self.session.query(Node).all()

        for i in xrange(0, len(nodes)):
            parent = nodes[i]

            if is_valid_parent(parent):
                self.assertIsInstance(create_node(self.session, type_=Section,
                                                  parent=parent), Section)
            else:
                self.assertRaises(ValueError, create_node, self.session,
                                  type_=Section, parent=parent)

            self.assertRaises(ValueError,create_node, self.session,
                              type_=NodeInfo, parent=parent)

            self.session.rollback()
