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


class NodeControllersTests(unittest.TestCase):

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
