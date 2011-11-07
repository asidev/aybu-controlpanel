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
                              Page)
from pyramid_handlers import action
import pyramid.security
from sqlalchemy.orm.exc import NoResultFound
from . base import BaseHandler
import copy
import logging


__all__ = ['StructureHandler']

log = logging.getLogger(__name__)


class StructureHandler(BaseHandler):

    _response_metadata = dict(root='dataset',
                              totalProperty='dataset_len',
                              idProperty='id',
                              successProperty='success',
                              fields=['id', 'button_label'])

    _response = dict(success=None,
                     dataset=None,
                     dataset_len=None,
                     message=None,
                     metaData=_response_metadata)

    @action(renderer='json',
            permission=pyramid.security.ALL_PERMISSIONS)
    def tree(self):
        language = self.request.language
        # FIXME: don't load all database!!!
        # HINT: add parameter 'level' to the request to load first N levels.
        return [node.to_dict(language)
                for node in Node.all(self.session)
                if isinstance(node, Menu) and node.parent == None]

    @action(renderer='string',
            permission=pyramid.security.ALL_PERMISSIONS)
    def link_list(self):
        """ Return a javascript with tinyMCELinkList array.
        """
        self.request.response.content_type = "application/javascript"
        try:
            language = self.request.language

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

    @action(renderer='json',
            permission=pyramid.security.ALL_PERMISSIONS)
    def list(self):

        response = copy.deepcopy(self._response)

        try:
            language = self.request.language

            response['dataset'] = [page.to_dict(language, recursive=False)
                                   for page in Page.all(self.session)]
            response['dataset_len'] = len(response['dataset'])

        except NoResultFound as e:
            log.exception('No language found.')
            self.request.response.status = 500
            response['dataset'] = []
            response['dataset_len'] = 0
            response['success'] = False
            response['message'] = str(e)

        else:
            self.request.response.status = 200
            response['success'] = True
            response['message'] = 'Page list retrieved.'

        return response


    @action(renderer='json',
            permission=pyramid.security.ALL_PERMISSIONS)
    def info(self):

        response = copy.deepcopy(self._response)

        try:
            language = self.request.language
            node = Node.get(self.session, int(self.request.params.get('id')))
            translation = node.get_translation(language)

        except (NoResultFound, TypeError, ValueError) as e:
            log.exception("Bad request.")
            response['data'] = None
            response['datalen'] = 0
            response['success'] = False
            response['message'] = str(e)
            self.request.response.status = 400

        except Exception as e:
            log.exception('Unknown error.')
            response['data'] = None
            response['datalen'] = 0
            response['success'] = False
            response['message'] = str(e)
            self.request.response.status = 500

        else:
            response['data'] = translation.to_dict()
            response['datalen'] = 1
            response['success'] = True
            response['message'] = 'Information retrieved.'
            self.request.response.status = 200

        return response

    @action(renderer='json',
            permission=pyramid.security.ALL_PERMISSIONS)
    def create(self):
        raise NotImplementedError

    @action(renderer='json',
            permission=pyramid.security.ALL_PERMISSIONS)
    def update(self):
        raise NotImplementedError

    @action(renderer='json', name='destroy',
            permission=pyramid.security.ALL_PERMISSIONS)
    def delete(self):
        raise NotImplementedError

    @action(renderer='json',
            permission=pyramid.security.ALL_PERMISSIONS)
    def move(self):
        raise NotImplementedError





