#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from aybu.core.models import Node, Menu, Page
from aybu.core.utils import get_object_from_python_path
from aybu.core.utils.exceptions import ValidationError, ConstraintError

log = logging.getLogger(__name__)


def create(session, cls, **params):
    """ Create a persistent 'cls' object and return it."""

    try:
        validator = 'aybu.controlpanel.libs.validators.node.validate_create'
        validator = get_object_from_python_path(validator)
    except ValueError as e:
        log.debug('A validator for %s does not exist!', cls.__name__, e)
    else:
        entity = cls(**validator(session, cls, **params))
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


# def delete(session, type_, **kwargs):
def delete(session, node_id):
    """
        Delete a node.
    """

    try:
        node = Node.get_by_id(session, node_id)
        log.debug('Deleting %s', node)

        if isinstance(node, Menu):
            error_message = "You can't remove Menu from here"
            log.warn(error_message)
            raise ValidationError(error_message)

        if isinstance(node, Page) and Page.is_last_page(session):
            error_message = "Cannot remove last page"
            log.warn(error_message)
            raise ConstraintError(error_message)

        old_weight = node.weight

        # set the node weight to a very high value so that it is "out" of
        # the tree
        node.weight = 696969
        session.flush()

        brothers_q = session.query(Node).filter(Node.parent == node.parent).\
                             filter(Node.id != node.id)

        children_q = session.query(Node).filter(Node.parent == node)

        num_children = children_q.count()
        num_brothers = brothers_q.count()

        log.debug("Num children %d", num_children)
        log.debug("Num brothers %d", num_brothers)

        log.debug("Making room for children nodes of the node to delete")
        # Update weight for those "brothers" of the node we are about to delete
        # in order to make room for its children to avoid duplicated weight
        # entries for the same parent
        brothers_q.filter(Node.weight > old_weight).update(
            values={Node.weight: Node.weight + num_children + num_brothers}
        )
        session.flush()

        log.debug("Moving old children")
        # Relocate node children up one level, adjusting their weight so they
        # take over to their father position

        children_q.update(values={
            Node.weight: old_weight + Node.weight - 1,
            Node.parent_id: node.parent_id
        })

        log.debug("Compacting nodes")
        # Move back node's brothers to compact node weights
        brothers_q.filter(Node.weight > old_weight + num_children - 1).\
                update(values={Node.weight: Node.weight - (num_brothers + 1)})

        session.flush()

        # TODO calculate and check new URLs of children

        # Due to db cascading this code should not be needed
        for translation in node.translations:
            session.delete(translation)

        log.debug("Deleting node")

        session.delete(node)

        session.commit()

        # TODO FLUSH CACHE (at least varnish)

    except Exception as e:
        log.exception(e)
        session.rollback()
        raise e


def index(session, type_, **kwargs):
    """
        Retrieve and return data to display menus trees.
        HINT: load __FIRST__ level of each menu.
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


def move(session, node_id, new_parent_id, previous_node_id):
    """
        Move a node
    """
    try:
        node = Node.get_by_id(session, node_id)
        old_parent = node.parent

        new_parent = Node.get_by_id(session, new_parent_id)

        if isinstance(node, Menu):
            error_message = "Root nodes can not be moved"
            log.warn(error_message)
            raise ValidationError(error_message)

        log.debug("Node to move has id %d, "
                  "had parent with id %d and had weight %d",
                  node.id, old_parent.id, node.weight)
        log.debug('New parent will be %s', new_parent)

        # get siblings in destination tree so that we can compute weights
        try:
            previous_node = Node.get_by_id(session, previous_node_id)
        except Exception as e:
            log.debug('Moved Node %s has no previous sibling', node)
            previous_node = None

        # compute weight
        if (not previous_node is None):

            if new_parent == old_parent and \
               previous_node.weight + 1 == node.weight:
                # The node was not moved
                log.debug('The node was not moved')
                return dict(success=True)

            new_weight = previous_node.weight + 1

        else:
            new_weight = 1

        log.debug('New weight will be %d', new_weight)

        # Setting node weight to an high number to avoid collisions
        old_weight = node.weight
        node.weight = 696969
        session.flush()

        # Reordering old brothers
        brothers_q = session.query(Node).filter(Node.parent == node.parent).\
                                   filter(Node.id != node.id)
        heavy_bros = brothers_q.filter(Node.weight > old_weight)
        num_heavy_bros = heavy_bros.count()

        # Augment their weight first
        heavy_bros.update(
            values={Node.weight: Node.weight + num_heavy_bros}
        )
        # Flush db to inform db of new weights
        session.flush()
        # Move back to compact node weights
        heavy_bros.update(
            values={Node.weight: Node.weight - (num_heavy_bros + 1)}
        )

        # Reordering new brothers
        brothers_q = session.query(Node).filter(Node.parent == new_parent).\
                                filter(Node.id != node.id)
        heavy_bros = brothers_q.filter(Node.weight >= new_weight)
        num_heavy_bros = heavy_bros.count()

        # augment their weight first
        heavy_bros.update(
            values={Node.weight: Node.weight + (num_heavy_bros + 1)}
        )
        # flush db to inform db of new weights
        session.flush()
        # move back to compact node weights
        heavy_bros.update(
            values={Node.weight: Node.weight - (num_heavy_bros)}
        )

        log.debug("Moving Node with id %d to new weight %d with parent %d",
                  node.id, new_weight, new_parent.id)
        node.parent = new_parent
        node.weight = new_weight

        # TODO
        # Calculate new url and set them in NodeInfo
        # URL conflict

        session.commit()

    except ValidationError as e:
        raise e

    except Exception as e:
        session.rollback()
        log.exception("An error occured moving a node : %s", e)
        raise e
