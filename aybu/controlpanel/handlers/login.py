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

from aybu.core.models import Page
from pyramid_handlers import action
from pyramid.httpexceptions import HTTPFound
from . base import BaseHandler


__all__ = ['LoginHandler']


class LoginHandler(BaseHandler):
    def __init__(self, request):
        super(LoginHandler, self).__init__(request)
        # FIXME: removeme
        self.request.template_helper.node = self.session.query(Page).first()

    @action(renderer='/admin/login.mako')
    def show(self):
        return dict(page='login', message=None)

    @action()
    def login(self):
        return HTTPFound(location=self.request.route_url('admin', action="index"))

    @action()
    def logout(self):
        return HTTPFound(location="/")
