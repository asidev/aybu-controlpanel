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

from pyramid_handlers import action
from aybu.core.models import Language, Page
from aybu.core.utils.modifiers import urlify
from . base import BaseHandler


__all__ = ['AdminHandler']


class AdminHandler(BaseHandler):

    def __init__(self, request):
        super(AdminHandler, self).__init__(request)
        # FIXME: removeme
        self.request.template_helper.node = self.session.query(Page).first()

    @action(renderer='/admin/index.mako')
    def index(self):
        return dict(page='index')

    @action(renderer='/admin/languages.mako')
    def languages(self):
        return dict(page='languages', languages=Language.all(self.session))

    @action(renderer='/admin/password.mako')
    def password(self):
        # TODO submit form
        return dict(page='password', success=True,
                    result_message=None, errors=dict(old_password='',
                                                     repeat_password=''))

    @action(renderer='/admin/images.mako')
    def images(self):
        tiny = True if "tiny" in self.request.params else False
        return dict(page='images', tiny=tiny)

    @action(renderer='/admin/files.mako')
    def files(self):
        tiny = True if "tiny" in self.request.params else False
        return dict(page='files', tiny=tiny)

    @action(renderer='/admin/settings.mako')
    def settings(self):
        return dict(page='settings')

    @action(renderer='/admin/structure.mako')
    def structure(self):
        return dict(page='structure')

    @action(renderer='json')
    def page_banners(self):
        raise NotImplementedError

    @action(renderer='json')
    def remove_page_banners(self):
        raise NotImplementedError

    @action(renderer='json')
    def banner_logo(self):
        raise NotImplementedError

    @action(renderer='json', name="urlfy")
    def urlify(self):
        # FIXME change action name to urlify
        res = dict()
        name = self.request.params.get('name', '')
        try:
            res['name'] = urlify(name)

        except:
            res['name'] = ''
            res['success'] = False

        else:
            res['success'] = True

        finally:
            return res
