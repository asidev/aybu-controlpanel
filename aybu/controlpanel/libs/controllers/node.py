
from aybu.controlpanel.libs.utils import load_entity_from_string
import logging


log = logging.getLogger(__name__)


def index(session, type_, **kwargs):
    """
        Retrieve and return data to display menus trees.
        HINT: load __FIRST__ level of each menu.
    """
    # Check node type. 
    # Validate params (based on node type).
    # Call model function to get wanted data.
    return None

def create(session, type_, **kwargs):
    """
        Create and return a new node.
    """
    try:
        Entity = load_entity_from_string(type_)

    except ValueError as e:
        msg = 'type_: entity %s does not exist!' % type_
        log.debug(msg)
        raise TypeError(msg)

    try:
        validator = load_validator_from_string('validate_%s' % Entity.__name__)

    except ValueError as e:
        log.debug('A validator for %s does not exist!' % Entity.__name__)

    else:
        validator(**kwargs)

    entity = Entity(**params)
    session.add(entity)

    return entity

def update(session, type_, **kwargs):
    """
        Update and return a node.
    """
    # Check node type.
    # Validate params (based on node type).
    # Call model function to get wanted data.
    return None

def delete(session, type_, **kwargs):
    """
        Delete a node.
    """
    # Check node type.
    # Validate params (based on node type).
    # Call model function to get wanted data.
    return None

def search(session, type_, **kwargs):
    """
        Perform a search in node collection and return results.
    """
    # Check node type.
    # Validate params (based on node type).
    # Call model function to get wanted data.
    return None
