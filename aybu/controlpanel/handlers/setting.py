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

from aybu.core.htmlmodifier import remove_target_attributes
from aybu.core.models import Setting
from aybu.core.models import SettingType
from BeautifulSoup import BeautifulSoup
from pyramid_handlers import action
import pyramid.security
from sqlalchemy.orm.exc import NoResultFound
from . base import BaseHandler
import copy
import json
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

    @action(renderer='json',
           permission=pyramid.security.ALL_PERMISSIONS)
    def update(self):

        response = copy.deepcopy(self._response)
        response.pop('dataset')
        response.pop('dataset_len')
        response.pop('metaData')
        response.pop('message')
        response['errors'] = {}

        try:
            setting = json.loads(self.request.params['dataset'])

        except KeyError as e:
            log.exception('Unable to load JSON request.')
            setting = dict(name=self.request.params.get('name'),
                           value=self.request.params.get('value'))

        except (TypeError, ValueError) as e:
            self.session.rollback()
            log.exception('Bad request.')
            response['success'] = False
            response['errors']['exception'] = e
            self.request.response.status = 400

        try:
            value = setting['value']
            setting = Setting.get(self.session, setting['name'])

            if setting.type.raw_type == 'bool' and value == 'on':
                value = 'True'

            elif setting.type.raw_type == 'bool':
                value = 'False'

            elif setting.type.raw_type == 'html':
                # add smartquotes to prevent bsoup from translating smart-quotes
                # and other windows-specific characters
                soup = BeautifulSoup(value, smartQuotesTo=None)
                soup = remove_target_attributes(soup)
                value = unicode(soup)

            setting.value = value
            self.session.flush()
            # TODO: purge cache

        except (NoResultFound, TypeError) as e:
            log.exception('No setting found.')
            self.session.rollback()
            response['success'] = False
            response['errors']['exception'] = str(e)
            self.request.response.status = 400

        except Exception as e:
            log.exception('Cannot update the setting')
            self.session.rollback()
            response['success'] = False
            response['errors']['exception'] = str(e)
            self.request.response.status = 500

        else:
            response['success'] = True
            self.request.response.status = 200
            self.session.commit()

        return response

    @action(renderer='json',
           permission=pyramid.security.ALL_PERMISSIONS)
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

            response['dataset_len'] = Setting.count(self.session,
                                                    self.request.user)

            log.debug('Start: %s.', start)
            log.debug('Limit: %s.', limit)
            log.debug('Sort by: %s.', sort_by)
            log.debug('Sort order: %s.', sort_order)
            log.debug("Collection count: %s.", response['dataset_len'])

            response['dataset'] = []
            for setting in Setting.list(self.session,
                                        limit=limit, start=start,
                                        sort_by=sort_by, sort_order=sort_order,
                                        user=self.request.user):
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

    @action(renderer='json',
           permission=pyramid.security.ALL_PERMISSIONS)
    def info(self):
        """ Get details of setting 'name'.
        """
        response = copy.deepcopy(self._response)

        try:
            setting = Setting.get(self.session, self.request.params.get('name'))

        except (NoResultFound, TypeError) as e:
            log.exception('No setting found.')
            self.session.rollback()
            response['dataset'] = []
            response['dataset_len'] = 0
            response['success'] = False
            response['message'] = str(e)
            self.request.response.status = 400

        except Exception as e:
            log.exception('Unknown error.')
            self.session.rollback()
            response['dataset'] = []
            response['dataset_len'] = 0
            response['success'] = False
            response['message'] = str(e)
            self.request.response.status = 500

        else:
            response['dataset'] = [setting.to_dict()]
            response['dataset_len'] = 1
            response['success'] = True
            response['message'] = 'Setting retrieved successfully.'
            self.request.response.status = 200

        return response

    @action(renderer='json',
           permission=pyramid.security.ALL_PERMISSIONS)
    def types(self):
        """ List settings types in the database.
        """
        response = copy.deepcopy(self._response)
        response['metaData']['idProperty'] = 'name'
        response['metaData']['fields'] = ['name', 'raw_type']

        try:
            response['dataset'] = [type_.to_dict()
                                   for type_ in SettingType.all(self.session)]
            response['dataset_len'] = len(response['dataset'])
            response['success'] = True
            response['message'] = 'SettingType collection retrieved.'
            self.request.response.status = 200

        except Exception as e:
            log.exception(e)
            response['dataset'] = []
            response['dataset_len'] = 0
            response['success'] = False
            response['message'] = str(e)
            self.request.response.status = 500

        return response
