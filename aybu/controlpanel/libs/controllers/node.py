#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from aybu.core.models import Node, Menu
from aybu.core.utils.exceptions import ValidationError

log = logging.getLogger(__name__)


def create(session, cls, **params):
    """ Create a persistent 'cls' object and return it."""

    try:
        validator = 'aybu.controlpanel.libs.validators.node.validate_create'
        validator = get_object_from_python_path(validator)

    except ValueError as e:
        log.debug('A validator for %s does not exist!' % cls.__name__)

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


def delete(session, type_, **kwargs):
    """
        Delete a node.
    """
    # Check node type.
    # Validate params (based on node type).
    # Call model function to get wanted data.
    return None


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


def move(session, node_id, new_parent_id, previous_node_id, next_node_id):
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

        try:
            next_node = Node.get_by_id(session, next_node_id)
        except Exception as e:
            log.debug('Moved Node %s has no next sibling', node)
            next_node = None

        # compute weight
        if (not previous_node is None) and (not next_node is None):

            if new_parent == old_parent and \
               previous_node.weight + 1 == next_node.weight - 1 and \
               previous_node.weight + 1 == node.weight:
                # The node was not moved
                log.debug('The node was not moved')
                return dict(success=True)

            new_weight = next_node.weight

        elif not previous_node is None:
            new_weight = previous_node.weight + 1
        elif not next_node is None:
            # new_weight = next_node.weight - 1
            new_weight = next_node.weight
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

        session.commit()

    except ValidationError as e:
        raise e

    except Exception as e:
        session.rollback()
        log.exception("An error occured moving a node : %s", e)
        raise e
