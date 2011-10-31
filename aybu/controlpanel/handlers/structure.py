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

from aybu.core.models import (Language, 
                              Menu,
                              Node,
                              ExternalLink,
                              InternalLink,
                              Page)
from pyramid_handlers import action
from . base import BaseHandler
import logging


__all__ = ['StructureHandler']

log = logging.getLogger(__name__)


class StructureHandler(BaseHandler):

    @action(renderer='json')
    def tree(self):
        # FIXME: add beaker session.
        # language = Language.get(self.session, client_session['lang'].id)
        language = Language.get(self.session, 1)
        # FIXME: don't load all database!!!
        # HINT: add parameter 'level' to the request to load first N levels.
        return [node.to_dict(language)
                for node in Node.all(self.session) 
                if isinstance(node, Menu) and node.parent == None]

    @action(renderer='string')
    def link_list(self):
        """ Return a javascript with tinyMCELinkList array.
        """
        self.request.response.content_type = "application/javascript"
        try:
            # FIXME: add beaker session.
            # language = Language.get(self.session, client_session['lang'].id)
            language = Language.get(self.session, 1)

            items = []
            for page in Page.all(self.session):
                translation = page.get_translation(language)
                item = '["{}","{}"]'.format(translation.title.replace('"', "'"),
                                            translation.url)
                items.append(item)

            response = 'var tinyMCELinkList = new Array(%s);' % ', '.join(items)

        except Exception as e:
            log.exception(e)
            self.session.rollback()
            response = '/* ' + str(e) + ' */'
            self.request.response.status = 500

        else:
            self.session.commit()
            self.request.response.status = 200

        return response

    @action(renderer='json')
    def list(self):
        raise NotImplementedError

    @action(renderer='json')
    def info(self):
        raise NotImplementedError

    @action(renderer='json')
    def create(self):
        raise NotImplementedError

    @action(renderer='json')
    def update(self):
        raise NotImplementedError

    @action(renderer='json', name='destroy')
    def delete(self):
        raise NotImplementedError

    @action(renderer='json')
    def move(self):
        raise NotImplementedError





