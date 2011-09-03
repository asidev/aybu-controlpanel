
from pyramid import testing
import logging
try:
    import unittest2 as unittest
except:
    import unittest


log = logging.getLogger(__name__)


class UtilsTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_load_entity_from_string(self):

        from aybu.controlpanel.models import Node
        from aybu.controlpanel.models import NodeInfo
        from aybu.controlpanel.libs.utils import load_entity_from_string

        self.assertRaises(ValueError,
                          load_entity_from_string, None)

        self.assertRaises(ValueError,
                          load_entity_from_string, '')

        for name, entity in {'Node': Node, 'NodeInfo': NodeInfo}.iteritems():

            self.assertEqual(entity,
                             load_entity_from_string(name))

            self.assertRaises(ValueError,
                              load_entity_from_string, name.lower())

            self.assertRaises(ValueError,
                              load_entity_from_string, name.upper())
