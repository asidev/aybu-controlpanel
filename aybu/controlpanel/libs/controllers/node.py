#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

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
