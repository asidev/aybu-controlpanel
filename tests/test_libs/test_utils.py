
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

        self.assertRaises(ValueError,
                          load_entity_from_string, 'dummy_entity_name')

        for name, entity in {'Node': Node, 'NodeInfo': NodeInfo}.iteritems():

            self.assertEqual(entity,
                             load_entity_from_string(name))

    def test_load_validator_from_string(self):

        from aybu.controlpanel.libs.utils import load_validator_from_string
        from aybu.controlpanel.libs.validators import validate_lineage
        from aybu.controlpanel.libs.validators import validate_node

        self.assertRaises(ValueError,
                          load_validator_from_string, None)

        self.assertRaises(ValueError,
                          load_validator_from_string, '')

        self.assertRaises(ValueError,
                          load_validator_from_string, 'dummy_validator_name')

        for name, validator in {'validate_lineage': validate_lineage,
                                'validate_node': validate_node}.iteritems():

            self.assertEqual(validator,
                             load_validator_from_string(name))
