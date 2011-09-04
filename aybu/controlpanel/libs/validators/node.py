
from aybu.controlpanel.models import Page, Menu, Section

def validate_lineage(cls, ancestor):
    """Check if 'cls' is a subclass of 'ancestor'.

    """

    if not issubclass(cls, ancestor):
        raise ValueError('%s is not a subclass of %s.' % (cls.__name__,
                                                          ancestor.__name__))

def validate_node(id=None, enabled=None, hidden=None, weight=None, 
                  parent=None, children=None):

    """ Validate input values that can be used to create a Node instance.

        Function signature contains all attributes of Node
        but 'id', 'enabled', 'hidden', 'weight' and 'children' are not checked.
    """
    if not isinstance(parent, (Menu, Section, Page)):
        raise ValueError('parent: %s cannot have children.' % parent.__name__)
