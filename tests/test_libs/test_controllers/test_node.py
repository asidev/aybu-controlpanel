
from pyramid import testing
import logging
try:
    import unittest2 as unittest
except:
    import unittest


log = logging.getLogger(__name__)


class NodeControllersTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

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
