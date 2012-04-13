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
from aybu.core.models import PageBanner
from aybu.core.utils.modifiers import urlify
from pyramid_handlers import action
from . base import BaseHandler
from sqlalchemy.orm.exc import NoResultFound
import pyramid.security
import collections
import json


__all__ = ['PageBannerHandler']


class PageBannerHandler(BaseHandler):

    _response = dict(success=False, msg='', dataset=[], dataset_length=0)

    @action(renderer='json',
            permission=pyramid.security.ALL_PERMISSIONS)
    def create(self):

        response = self._response.copy()

        try:

            # Convert JSON request param into dictionary.
            params = json.loads(self.request.params['dataset'])
            if not isinstance(params, collections.Sequence):
                params = [params]

            items = []
            for param in params:
                obj = PageBanner(node_id=param['page_id'], file_id=param['file']['id'])
                self.session.add(obj)
                items.append(obj.dictify())

        except KeyError as e:
            self.log.exception('Missing params in the request.')
            self.session.rollback()
            self.request.response.status = 400
            response['msg'] = self.request.translate("Missing parameters.")

        except Exception as e:
            self.log.exception('Unknown error.')
            self.session.rollback()
            self.request.response.status = 500
            response['msg'] = str(e)

        else:
            self.session.commit()
            response['success'] = True
            response['dataset'] = items
            response['dataset_length'] = len(response['dataset'])
            response['msg'] = self.request.translate("PageBanner was created.")

        finally:
            return response

    @action(renderer='json',
            permission=pyramid.security.ALL_PERMISSIONS)
    def read(self):

        response = self._response.copy()

        try:
            page_id = self.request.params['page_id']
            page = Page.get(self.session, page_id)
            items = [obj.dictify() for obj in page.banners]

        except KeyError as e:
            self.log.exception('Not URL param in the request.')
            self.session.rollback()
            self.request.response.status = 400
            response['msg'] = self.request.translate("Missing parameter: 'url'.")

        except NoResultFound as e:
            msg = "No Page found: %s" % page_id
            self.log.exception(msg)
            self.session.rollback()
            self.request.response.status = 404
            response['msg'] = self.request.translate(msg)

        except Exception as e:
            self.log.exception('Unknown error.')
            self.session.rollback()
            self.request.response.status = 500
            response['msg'] = str(e)

        else:
            self.session.commit()
            response['success'] = True
            response['dataset'] = items
            response['dataset_length'] = len(response['dataset'])
            response['msg'] = self.request.translate("Page was found.")

        finally:
            return response

    @action(renderer='json',
            permission=pyramid.security.ALL_PERMISSIONS)
    def delete(self):

        response = self._response.copy()

        try:
            node_id = self.request.matchdict['node_id']
            file_id = self.request.matchdict['file_id']
            PageBanner.get(self.session, (node_id, file_id)).delete()

        except KeyError as e:
            self.log.exception('Missing ID param in the request.')
            self.session.rollback()
            self.request.response.status = 400
            response['msg'] = self.request.translate("Missing ID parameter.")

        except NoResultFound as e:
            msg = "No PageBanner found: %s, %s" % (node_id, file_id)
            self.log.exception(msg)
            self.session.rollback()
            self.request.response.status = 404
            response['msg'] = self.request.translate(msg)

        except Exception as e:
            self.log.exception('Unknown error.')
            self.session.rollback()
            self.request.response.status = 500
            response['msg'] = str(e)

        else:
            self.session.commit()
            response['success'] = True
            response['msg'] = self.request.translate("PageBanner was found.")

        finally:
            return response
