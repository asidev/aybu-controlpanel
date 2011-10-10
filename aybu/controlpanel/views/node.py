#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright 2010 Asidev s.r.l.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import logging
from aybu.core.utils import get_object_from_python_path


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
        Entity = get_object_from_python_path('aybu.core.models.%s'
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


def move(context, request):
    """
        This views is called to move a node.
    """
    # Parsing the request
    try:
        moved_node_id = int(request.params.get('moved_node_id', None))
        parent_id = int(request.params.get('new_parent_id', None))

        try:
            previous_node_id = int(request.params.get('previous_node_id',
                                                      None))
        except:
            previous_node_id = None

        aybu.controlpanel.libs.controllers.node.move(request.db_session,
                                                     moved_node_id,
                                                     parent_id,
                                                     previous_node_id)

    except Exception as e:
        log.exception("An error occured moving a menu entry : %s", e)
        res = _(u"Si è verificato un errore nello spostamento della voce di menù richiesta")
        #response.status = 500


    # Call controller move.
    # Prepare response
    return None
