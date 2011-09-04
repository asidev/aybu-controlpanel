
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

    def test_get_object_from_python_path(self):

        from aybu.controlpanel.libs.utils import get_object_from_python_path
        from aybu.controlpanel.libs.validators import validate_lineage
        from aybu.controlpanel.libs.validators import validate_node
        from aybu.controlpanel.models import Node
        from aybu.controlpanel.models import NodeInfo

        self.assertRaises(ValueError,
                          get_object_from_python_path, None)

        self.assertRaises(ValueError,
                          get_object_from_python_path, '')

        self.assertRaises(ValueError,
                          get_object_from_python_path, 'wrong_name')

        path = 'aybu.controlpanel.models.Node'
        self.assertEqual(Node,
                         get_object_from_python_path(path))

        path = 'aybu.controlpanel.models.NodeInfo'
        self.assertEqual(NodeInfo,
                         get_object_from_python_path(path))

        path = 'aybu.controlpanel.libs.validators.validate_lineage'
        self.assertEqual(validate_lineage,
                         get_object_from_python_path(path))

        path = 'aybu.controlpanel.libs.validators.validate_node'
        self.assertEqual(validate_node,
                         get_object_from_python_path(path))

        path = 'aybu.controlpanel.libs.validators.wrong_name'
        self.assertRaises(ValueError,
                          get_object_from_python_path, path)
