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
from aybu.controlpanel.lib.structure import check_url_part

log = getLogger(__name__)


class ModelsTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

        """
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
        """

    def tearDown(self):
        self.session.remove()
        testing.tearDown()


class StructureTests(ModelsTests):

    def test_check_url_part(self):

        title = 'La nostra storia'

        url_part = 'La nostra storia'

        correct_url_part = 'la_nostra_storia'

        generated_url_part = check_url_part(url_part, title)

        # Check if the calculated url is equal to the expected result
        self.assertEqual(correct_url_part, generated_url_part)

        # Check no spaces are in result
        self.assertNotIn(' ', generated_url_part)

        # Check no capital letter in result
        pattern = "[A-Z]"
        assertNotRegexpMatches(generated_url_part, pattern)






