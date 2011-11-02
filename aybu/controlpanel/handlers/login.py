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

from aybu.core.models import Page, User
from pyramid_handlers import action
from pyramid.httpexceptions import HTTPFound
from . base import BaseHandler
import pyramid.security


__all__ = ['LoginHandler']


class LoginHandler(BaseHandler):
    def __init__(self, request):
        super(LoginHandler, self).__init__(request)
        # FIXME: removeme
        self.request.template_helper.node = self.session.query(Page).first()

    @action(renderer='/admin/login.mako')
    def login(self):
        res = dict(message=None, page='login')
        if self.request.params.get('submit') is None:
            self.log.debug("User: %s", self.request.user)
            self.log.debug("Session: %s", self.request.session.keys())
            if not self.request.user is None:
                return HTTPFound(location=self.request.route_url('admin',
                                                                 action='index'))
            else:
                return res

        try:
            username = self.request.params['username']
            password = self.request.params['password']
            User.check(self.request.db_session, username, password)

        except:
            self.log.exception('Invalid Login')
            message = u'Username o password non validi'
            res['message'] = self.request.translate(message)
            self.request.response.status_int = 400
            return res

        else:
            pyramid.security.remember(self.request, username)
            return HTTPFound(location=self.request.route_url('admin',
                                                             action="index"))

    @action(permission=pyramid.security.ALL_PERMISSIONS)
    def logout(self):
        pyramid.security.forget(self.request)
        return HTTPFound(location="/")
