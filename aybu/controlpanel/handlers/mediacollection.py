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
from . base import BaseHandler
from sqlalchemy.orm.exc import NoResultFound
import pyramid.security


__all__ = ['MediaCollectionHandler']


class MediaCollectionHandler(BaseHandler): pass
"""
    _response = dict(success=False, msg='', dataset=[], dataset_length=0)

    @action(renderer='json',
            permission=pyramid.security.ALL_PERMISSIONS)
    def create(self):

        response = self._response.copy()

        try:
            page_id = self.request.params['page_id']
            self.log.debug('Page ID found: %s.', page_id)
            page = Page.get(self.session, page_id)
            self.log.debug('Page found: %s.', page)
            label = self.request.params['label']
            caption = self.request.params.get('caption')
            file_ = self.request.params.get('file')
            language = self.request.language
            collection = MediaCollection(page=page)
            self.session.add(collection)
            collection_info = MediaCollectionInfo(label=label,
                                                  caption=caption,
                                                  node=collection)
            self.session.add(collection_info)
            self.log.debug(collection)

        except KeyError as e:
            self.log.exception('Bad request.')
            self.session.rollback()
            self.request.response.status = 400
            response['msg'] = self.request.translate("One or more parameters missing.")

        except NoResultFound as e:
            self.log.exception('No Page: %s.', page_id)
            self.session.rollback()
            self.request.response.status = 404
            response['msg'] = self.request.translate("No Page found.")

        except Exception as e:
            self.log.exception('Unknown error.')
            self.session.rollback()
            self.request.response.status = 500
            response['msg'] = str(e)

        else:
            self.session.commit()
            response['success'] = True
            response['dataset'] = []#[collection]
            response['dataset_length'] = len(response['dataset'])
            response['msg'] = self.request.translate("Language found.")

        finally:
            return response
"""
