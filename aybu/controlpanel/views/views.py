#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aybu.controlpanel.lib.structure import create_node


def homepage(context, request):
    return {'content': 'Secret content'}


def login(context, request):
    return {}

def create_site_node(context, request):

    # Parsing the request

    params = {}

    create_node(request.db_session, **params)

    # Prepare response
    pass
