#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from aybu.controlpanel.libs.utils import get_object_from_python_path


log = logging.getLogger(__name__)

__all__ = []


def index(context, request):
    """
        This views is called when the user enters in
        the control panel section named "Pages management".
        The view must load data to display menus trees.
        HINT: load __FIRST__ level of each menu.
    """
    # Parsing the request
    # Call controller index to list node tree: don't load all tree!!!
    # Prepare response
    return None


def create(context, request):
    """
        This views is called to create a new node.
        Node type must be specified.
    """
    type_ = request.params.pop('type_', None)
    # Pop keys from 'request.params':
    # you cannot send variables to the controller that are not needed.

    try:
        Entity = get_object_from_python_path('aybu.controlpanel.models.%s'
                                             % (type_))

    except ValueError as e:
        msg = 'type_: entity %s does not exist!' % type_
        log.debug(msg)
        # FIXME: raise the right HTTP exception!
        raise TypeError(msg)

    else:
        controller = 'aybu.controlpanel.libs.controllers.node.create'

    try:
        controller = get_object_from_python_path(controller)

    except ValueError as e:
        log.debug('A controller for %s does not exist!' % Entity.__name__)
        # FIXME: raise the right HTTP exception!
        log.debug(e)
        raise e

    else:
        entity = controller(request.db_session, Entity, **request.params)

    # Prepare response
    return None


def update(context, request):
    """
        This views is called to update a node.
        Node id and type must be specified.
    """
    # Parsing the request
    # Call controller update.
    # Prepare response
    return None


def delete(context, request):
    """
        This views is called to delete node.
        Node id and type must be specified.
    """
    # Parsing the request
    # Call controller delete.
    # Prepare response
    return None


def search(context, request):
    """
        This views is called to perform a search in node collection.
    """
    # Parsing the request
    # Call controller update.
    # Prepare response
    return None
