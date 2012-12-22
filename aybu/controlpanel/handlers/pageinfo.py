#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright 2010-2012 Asidev s.r.l.

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

from aybu.core.models import PageInfo
from pyramid_handlers import action
from . base import BaseHandler
from urlparse import urlparse
from sqlalchemy.orm.exc import NoResultFound
import pyramid.security


__all__ = ['PageInfoHandler']


class PageInfoHandler(BaseHandler):

    _response = dict(success=False, msg='', dataset=[], dataset_length=0)

    @action(renderer='json',
            permission=pyramid.security.ALL_PERMISSIONS)
    def search(self):
        response = self._response.copy()
        try:
            url = urlparse(self.request.params['url'])
            path = url.path
            if path.startswith('/admin'):
                path = path.replace('/admin', '', 1)
            if path.endswith('.html'):
                path = path.replace('.html', '', 1)
            pageinfo = PageInfo.get_by_url(self.session, path)
            self.log.debug('Found %s using %s', pageinfo, path)
            pageinfo = pageinfo.dictify(excludes=('__class__',
                                                  'meta_description',
                                                  'title',
                                                  'head_content',
                                                  '_parent_url',
                                                  'label', 'content',
                                                  'url_part',
                                                  'discriminator'))

        except KeyError as e:
            self.log.exception('Not URL param in the request.')
            self.session.rollback()
            self.request.response.status = 400
            response['msg'] = self.request.translate("Missing parameter: 'url'.")

        except NoResultFound as e:
            self.log.exception('No PageInfo: %s.', path)
            self.session.rollback()
            self.request.response.status = 404
            response['msg'] = self.request.translate("No PageInfo found.")

        except Exception as e:
            self.log.exception('Uknown error.')
            self.session.rollback()
            self.request.response.status = 500
            response['msg'] = str(e)

        else:
            self.session.commit()
            response['success'] = True
            response['dataset'] = [pageinfo]
            response['dataset_length'] = len(response['dataset'])
            response['msg'] = self.request.translate("PageInfo found.")

        finally:
            return response
