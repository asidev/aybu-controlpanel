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


log = logging.getLogger(__name__)

__all__ = []


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
