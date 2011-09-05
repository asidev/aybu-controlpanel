#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyramid.security


class Authenticated(object):

    __acl__ = [(pyramid.security.Allow,
                pyramid.security.Authenticated,
                pyramid.security.ALL_PERMISSIONS),
                pyramid.security.DENY_ALL]

    def __init__(self, request): pass
