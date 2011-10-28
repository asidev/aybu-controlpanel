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

from aybu.core.models import Setting
from pyramid_handlers import action
from . base import BaseHandler
import copy
import logging


__all__ = ['SettingHandler']

log = logging.getLogger(__name__)

class SettingHandler(BaseHandler):

    _response_metadata = dict(root='dataset',
                              totalProperty='dataset_len',
                              idProperty='id',
                              batch=True,
                              remoteSort=True,
                              start='start',
                              limit='limit',
                              successProperty='success',
                              fields=['name',
                                      'value',
                                      'raw_type',
                                      'setting_type_name',
                                      'ui_administrable'])

    _response = dict(success=None,
                     dataset=None,
                     dataset_len=None, 
                     message=None,
                     metaData=_response_metadata)

    @action(renderer='json')
    def update(self):
        raise NotImplementedError

    @action(renderer='json')
    def list(self):
        """ List settings in the database.
            Result set can be ordered and/or paginated.
            Result set is filtered by Setting.ui_administrable 
            when debug is True.
        """

        response = copy.deepcopy(self._response)

        try:
            start = self.request.params.get('start')
            start = None if start is None else int(start)
            limit = self.request.params.get('limit')
            limit = None if limit is None else int(limit)
            sort_by = self.request.params.get('sort')
            sort_order = self.request.params.get('dir', 'desc').lower()

            debug = Setting.get(self.session, 'debug').value
            response['dataset_len'] = Setting.count(self.session,
                                                    ui_administrable=debug)

            log.debug('Start: %s.', start)
            log.debug('Limit: %s.', limit)
            log.debug('Sort by: %s.', sort_by)
            log.debug('Sort order: %s.', sort_order)
            log.debug("Setting 'debug': %s.", debug)
            log.debug("Collection count: %s.", response['dataset_len'])

            response['dataset'] = []
            for setting in Setting.list(self.session,
                                        ui_administrable=debug,
                                        limit=limit, start=start,
                                        sort_by=sort_by, sort_order=sort_order):
                response['dataset'].append(setting.to_dict())

            log.debug("Dataset length: %s.", len(response['dataset']))

            self.request.response.status = 200
            response['success'] = True
            response['message'] = 'Dataset retrieved.'

        except ValueError as e:
            self.request.response.status = 400
            response['success'] = False
            response['message'] = 'Invalid start and/or limit'
            log.exception(response['message'])

        except Exception as e:
            log.exception('Unable to query on settings collection.')
            self.request.response.status = 500
            response['success'] = False
            response['message'] = str(e)

        return response

    @action(renderer='json')
    def info(self):
        raise NotImplementedError

    @action(renderer='json')
    def types(self):
        raise NotImplementedError

