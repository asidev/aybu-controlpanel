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

from aybu.core.models import Language, View
from pyramid_handlers import action
import pyramid.security
from . base import BaseHandler
import logging


__all__ = ['ViewHandler']
log = logging.getLogger(__file__)


class ViewHandler(BaseHandler):

    _response_metadata = dict(root='dataset',
                              totalProperty='dataset_len',
                              idProperty='id',
                              successProperty='success',
                              fields=['id', 'description'])
    _response = dict(metaData=_response_metadata,
                     success=True,
                     dataset=[],
                     dataset_len=0)

    def _list(self, session):

        # FIXME: adjust when there will be a session
        language = Language.first(self.session)
        # language = session['lang']

        items = []

        for view in View.all(session):

            item = dict(id=view.id, description=None)

            if not view.descriptions:
                raise RuntimeError('View %s has no description in any language',
                                    view.id)

            descriptions = [description
                            for description in view.descriptions
                            if description.language == language]

            if descriptions:
                item['description'] = descriptions[0].description

            else:
                item['description'] = view.descriptions[0].description

            items.append(item)

        log.debug(items)

        return items

    @action(renderer='json',
            permission=pyramid.security.ALL_PERMISSIONS)
    def list(self):

        response = self._response.copy()

        try:
            response['dataset'].extend(self._list(self.session))
            response['dataset_len'] = len(response['dataset'])
            self.request.response.status = 200

        except Exception as e:
            log.exception(e)
            response['success'] = False
            response['message'] = str(e)
            self.request.response.status = 500

        return response
