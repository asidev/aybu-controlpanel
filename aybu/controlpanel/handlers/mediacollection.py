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

from aybu.core.exc import QuotaError
from aybu.core.models import (Image,
                              Node,
                              MediaCollectionPage,
                              MediaCollectionPageInfo,
                              MediaItemPage,
                              MediaItemPageInfo,
                              View)
from aybu.core.utils.modifiers import urlify
from aybu.website.lib import get_pufferfish_paths
from pyramid_handlers import action
from . base import BaseHandler
from sqlalchemy.orm.exc import NoResultFound
import pyramid.security
from urlparse import urlparse
import collections
from functools import partial
import json


__all__ = ['MediaCollectionPageHandler']


class MediaCollectionPageHandler(BaseHandler):

    _response = dict(success=False, msg='', dataset=[], dataset_length=0)

    @action(renderer='/plugins/mediacollection/mediacollectionpage.mako',
            permission=pyramid.security.ALL_PERMISSIONS)
    def show_html_view(self):

        response = dict(language=self.request.language,
                        get_paths_for=partial(get_pufferfish_paths,
                                              self.request),
                        items=[])

        try:
            collection = MediaCollectionPage.get(self.session,
                                                 self.request.matchdict['id'])

        except KeyError as e:
            self.log.exception('Missing params in the request.')
            self.session.rollback()
            self.request.response.status = 400
            response['msg'] = self.request.translate("Missing parameters.")

        except NoResultFound as e:
            msg = "No MediaCollectionPage found."
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
            response['node'] = collection

        finally:
            return response


class MediaItemPageHandler(BaseHandler):

    _response = dict(success=False, msg='', dataset=[], dataset_length=0)

    def _create(self, params):

            parent_url = urlparse(params['parent_url']).path
            if parent_url.startswith('/admin'):
                parent_url = parent_url.replace('/admin', '', 1)
            parent_url = parent_url.rsplit('.', 1)[0]

            node_info = MediaCollectionPageInfo.get_by_url(self.session,
                                                           parent_url)

            # Node attributes.
            enabled = params.get('enabled', 'on')
            enabled = True if enabled.lower() == 'on' else False
            hidden = params.get('hidden', 'off')
            hidden = True if hidden.lower() == 'on' else False
            max_weight = Node.get_max_weight(self.session, node_info.node)
            weight = params.get('weight', max_weight)
            #self.log.debug(max_weight)
            weight = int(weight) + 1
            # Page attributes.
            home = params.get('home', 'off')
            home = True if home.lower() == 'on' else False
            sitemap_priority = params.get('sitemap_priority')
            sitemap_priority = int(sitemap_priority) if sitemap_priority else 1
            # FIXME: add the right view needed by MediaItemPage rendering.
            view = View.get(self.session, 1)
            file_id = params.get('file', {}).get('id')

            node = MediaItemPage(enabled=enabled,
                                 hidden=hidden,
                                 parent=node_info.node,
                                 weight=weight,
                                 home=home,
                                 sitemap_priority=sitemap_priority,
                                 view=view,
                                 file_id=file_id)

            # NodeInfo attributes.
            translation = params.get('translations')[0]
            label = translation['label']
            language = self.request.language
            # CommonInfo attributes.
            title = translation.get('title', label)
            url_part = translation.get('url_part', title).strip()
            url_part = urlify(url_part)
            meta_description = translation.get('meta_description')
            head_content = translation.get('head_content')
            # Page attributes.
            content = translation.get('content', '')

            node_info = MediaItemPageInfo(label=label,
                                          node=node,
                                          lang=language,
                                          title=title,
                                          url_part=url_part,
                                          meta_description=meta_description,
                                          head_content=head_content,
                                          content=content)

            self.session.add(node)
            self.session.add(node_info)
            node_info.translate(enabled_only=True)

            return node

    @action(renderer='json',
            permission=pyramid.security.ALL_PERMISSIONS)
    def create(self):

        response = self._response.copy()

        try:

            if not MediaItemPage.new_page_allowed:
                raise QuotaError('New pages are not allowed.')

            # Convert JSON request param into dictionary.
            params = json.loads(self.request.params['dataset'])
            if not isinstance(params, collections.Sequence):
                params = [params]

            items = []
            for param in params:
                item = self._create(param)
                dictified = item.dictify()
                dictified['file'] = {}
                if not item.file is None:
                    item.file.set_paths(**get_pufferfish_paths(self.request,
                                                               Image))
                    dictified['file'] = item.file.to_dict()
                dictified['translations'] = [
                        t.dictify() for t in item.translations
                                    if t.lang == self.request.language]
                items.append(dictified)

        except KeyError as e:
            self.log.exception('Missing params in the request.')
            self.session.rollback()
            self.request.response.status = 400
            response['msg'] = self.request.translate("Missing parameters.")

        except QuotaError as e:
            self.log.exception('Quota Error.')
            self.session.rollback()
            self.request.response.status = 500
            response['errors'] = {}
            response['success'] = False
            response['errors']['500'] = 'Maximum pages number reached.'

        except NoResultFound as e:
            msg = "No MediaCollectionPageInfo found."
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
            response['msg'] = self.request.translate("MediaItemPageInfo found")

        finally:
            return response

    @action(renderer='json',
            permission=pyramid.security.ALL_PERMISSIONS)
    def search(self):

        response = self._response.copy()

        try:
            parent_url = urlparse(self.request.params['parent_url']).path
            if parent_url.startswith('/admin'):
                parent_url = parent_url.replace('/admin', '', 1)

            parent_url = parent_url.rsplit('.', 1)[0]
            info = MediaCollectionPageInfo.get_by_url(self.session, parent_url)
            items = []
            for item in info.node.children:
                dictified = item.dictify()
                dictified['file'] = {}
                if not item.file is None:
                    item.file.set_paths(**get_pufferfish_paths(self.request,
                                           Image))
                    dictified['file'] = item.file.to_dict()
                dictified['translations'] = [
                        t.dictify() for t in item.translations
                                    if t.lang == self.request.language]
                items.append(dictified)

        except KeyError as e:
            self.log.exception('Not URL param in the request.')
            self.session.rollback()
            self.request.response.status = 400
            response['msg'] = self.request.translate("Missing parameter 'url'")

        except NoResultFound as e:
            msg = "No MediaPageInfo found: %s" % parent_url
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
            response['msg'] = self.request.translate("MediaItemPageInfo found")

        finally:
            return response

    @action(renderer='json',
            permission=pyramid.security.ALL_PERMISSIONS)
    def delete(self):

        response = self._response.copy()

        try:
            id_ = self.request.matchdict['id']
            MediaItemPage.delete(self.session, id_)

        except KeyError as e:
            self.log.exception('Not ID param in the request.')
            self.session.rollback()
            self.request.response.status = 400
            response['msg'] = self.request.translate("Missing parameter 'id'")

        except NoResultFound as e:
            msg = "No MediaItemPage found: %s" % id_
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
            response['dataset'] = [id_]
            response['dataset_length'] = len(response['dataset'])
            response['msg'] = self.request.translate("MediaItemPage found")

        finally:
            return response

    @action(renderer='json',
            permission=pyramid.security.ALL_PERMISSIONS)
    def update(self):

        response = self._response.copy()

        try:
            id_ = self.request.matchdict['id']
            MediaItemPage.get(self.session, id_)
            # Convert JSON request param into dictionary.
            params = json.loads(self.request.params['dataset'])
            translation = params['translations'][0]
            info = MediaItemPageInfo.get(self.session, translation['id'])
            info.label = translation['label']
            info.title = info.label
            info.url_part = urlify(info.title)
            info.content = translation['content']

        except KeyError as e:
            self.log.exception('Not ID param in the request.')
            self.session.rollback()
            self.request.response.status = 400
            response['msg'] = self.request.translate("Missing parameter: 'id'")

        except NoResultFound as e:
            msg = "No MediaItemPage found: %s" % id_
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
            response['dataset'] = [id_]
            response['dataset_length'] = len(response['dataset'])
            response['msg'] = self.request.translate("MediaItemPage updated")

        finally:
            return response
