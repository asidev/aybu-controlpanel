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
from aybu.core.utils.modifiers import urlify
from aybu.core.models import (Language,
                              Menu,
                              Node,
                              ExternalLink,
                              InternalLink,
                              Page,
                              Section,
                              ExternalLinkInfo,
                              InternalLinkInfo,
                              PageInfo,
                              SectionInfo,
                              View)
from pyramid_handlers import action
import pyramid.security
from sqlalchemy.orm.exc import (NoResultFound,
                                MultipleResultsFound)
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

        response = copy.deepcopy(self._response)

        try:
            language = self.request.language
            type_ = self.request.params.get('type') # Specify model entity.

            # Node attributes.
            enabled = self.request.params.get('enabled', 'off')
            enabled = True if enabled.lower() == 'on' else False

            # FIXME: check JS to verify 'hidden' support.
            hidden = self.request.params.get('hidden', 'off')
            hidden = True if hidden.lower() == 'on' else False
            parent = self.request.params.get('parent_id')
            parent = None if parent is None else Node.get(self.session, parent)
            weight = self.request.params.get('weight',
                                             Node.get_max_weight(self.session,
                                                                 parent))
            weight = int(weight) + 1

            # NodeInfo attributes
            label = self.request.params.get('button_label')

            # CommonInfo attributes.
            title = self.request.params.get('title', 'No title')
            url_part = self.request.params.get('url_part', title).strip()
            url_part = urlify(url_part)
            meta_description = self.request.params.get('meta_description')
            head_content = self.request.params.get('head_content')
            # Use 'partial_url' as 'parent_url'

            if type_ in ('Section', 'Page') and isinstance(parent,
                                                             (Section, Page)):

                parent_info = parent.get_translation(language)
                partial_url = '{}/{}'.format(parent_info.partial_url,
                                             parent_info.url_part)

            else:
                partial_url = '/{}'.format(language.lang)


            if type_ == 'Section':

                node = Section(enabled=enabled,
                               hidden=hidden,
                               parent=parent,
                               weight=weight)
                node_info = SectionInfo(label=label,
                                        node=node,
                                        lang=language,
                                        title=title,
                                        url_part=url_part,
                                        meta_description=meta_description,
                                        head_content=head_content,
                                        partial_url=partial_url)

            elif type_ == 'Page':
                # Page attributes.
                home = self.request.params.get('home', 'off')
                home = True if home.lower() == 'on' else False
                sitemap_priority = self.request.params.get('sitemap_priority')
                sitemap_priority = int(sitemap_priority)
                view = self.request.params.get('page_type_id')
                view = None if view is None else View.get(self.session, view)

                # PageInfo attributes.
                url = self.request.params.get('url',
                                              '{}/{}.html'.format(partial_url,
                                                                  url_part))

                if not Page.new_page_allowed:
                    raise QuotaError('New pages are not allowed.')

                try:
                    # Check for URL collisions.
                    page = PageInfo.get_by_url(self.session, url)

                except NoResultFound as e:
                    content = self.request.params.get('content',
                                                      u'<h2>{}</h2>'.format(title))

                    node = Page(enabled=enabled,
                                hidden=hidden,
                                parent=parent,
                                weight=weight,
                                home=home,
                                sitemap_priority=sitemap_priority,
                                view=view)
                    node_info = PageInfo(label=label,
                                         node=node,
                                         lang=language,
                                         title=title,
                                         url_part=url_part,
                                         meta_description=meta_description,
                                         head_content=head_content,
                                         partial_url=partial_url,
                                         content=content,
                                         url=url)
                else:
                    raise MultipleResultsFound('Pages URLs must be unique!')

            elif type_ == 'InternalLink':

                linked_to = self.request.params.get('linked_to')
                if not linked_to is None:
                    linked_to = InternalLink.get(self.session, linked_to)

                node = InternalLink(enabled=enabled,
                                    hidden=hidden,
                                    parent=parent,
                                    weight=weight,
                                    linked_to=linked_to)
                node_info = InternalLinkInfo(label=label,
                                             node=node,
                                             lang=language)

            elif type_ == 'ExternalLink':
                ext_url = self.request.params.get('external_url')
                node = ExternalLink(enabled=enabled,
                                    hidden=hidden,
                                    parent=parent,
                                    weight=weight)
                node_info = ExternalLinkInfo(label=label,
                                             node=node,
                                             lang=language,
                                             ext_url=ext_url)

            else:
                raise NotImplementedError('Cannot create: %s' % type_)

            self.session.add(node)
            self.session.add(node_info)
            node_info.translate(enabled_only=True)

        except NotImplementedError as e:
            log.exception('Not Implemented.')
            self.session.rollback()
            self.request.response.status = 501 # HTTP 501 Not Implemented Error.
            response['errors'] = {}
            response['success'] = False
            response['errors']['501'] = 'Cannot create %s entity.' % type_

        except QuotaError as e:
            log.exception('Quota Error.')
            self.session.rollback()
            self.request.response.status = 500
            response['errors'] = {}
            response['success'] = False
            response['errors']['500'] = 'Maximum pages number reached.'

        except MultipleResultsFound as e:
            log.exception('Pages URls must be unique.')
            self.session.rollback()
            self.request.response.status = 409
            response['errors'] = {}
            response['success'] = False
            response['errors']['409'] = str(e)

        except Exception as e:
            log.exception('Unknown Error.')
            self.session.rollback()
            self.request.response.status = 500
            response['errors'] = {}
            response['success'] = False
            response['errors']['500'] = str(e)

        else:
            self.session.commit()
            self.request.response.status = 200
            response['errors'] = {}
            response['dataset'] = [{'id': node.id}]
            response['dataset_len'] = 1
            response['success'] = True

        return response

    @action(renderer='json',
            permission=pyramid.security.ALL_PERMISSIONS)
    def update(self):

        response = copy.deepcopy(self._response)

        try:

            language = self.request.language
            node_id = int(self.request.params.get('id'))
            node = Node.get(self.session, node_id)
            info = node.get_translation(language)

            # Node attributes.
            enabled = self.request.params.get('enabled')
            if enabled is None:
                enabled = node.enabled
            else:
                enabled = True if enabled.lower() == 'on' else False
            # NodeInfo attributes
            label = self.request.params.get('button_label', info.label)
            # CommonInfo attributes.
            title = self.request.params.get('title', info.title)
            url_part = self.request.params.get('url_part', info.url_part).strip()
            url_part = urlify(url_part)
            meta_description = self.request.params.get('meta_description',
                                                       info.meta_description)
            head_content = self.request.params.get('head_content',
                                                   info.head_content)

            node.enabled = enabled
            info.title = title
            info.label = label
            info.meta_description = meta_description
            info.head_content = head_content

            if isinstance(node, (Page, Section)) and info.url_part != url_part:
                log.debug("Change url_part from '%s' to '%s'.",
                          info.url_part, url_part)
                info.url_part = url_part

            if isinstance(node, Page):
                node.view = View.get(self.session,
                                     int(request.params.get('page_type_id')))

            elif isinstance(node, InternalLink):
                node.linked_to = Node.get(self.session,
                                          int(request.params.get('linked_to')))

            elif isinstance(node, ExternalLink):
                ext_url = request.params.get('external_url', '')
                if not ext_url.startswith("http://"):
                    ext_url = 'http://' + ext_url
                info.ext_url = ext_url

            """ FIXME: purge cache.
            if routing_changed:
                reload_routing()
            else:
                aybu.cms.lib.cache.flush_all()
            """

        except (TypeError, NoResultFound) as e:
            log.exception('Bad request params.')
            self.session.rollback()
            self.request.response.status = 400
            response['errors'] = {}
            response['success'] = False
            response['errors']['400'] = str(e)

        except Exception as e:
            log.exception('Unknown Error.')
            self.session.rollback()
            self.request.response.status = 500
            response['errors'] = {}
            response['success'] = False
            response['errors']['500'] = str(e)

        else:
            self.session.commit()
            self.request.response.status = 200
            response['errors'] = {}
            response['dataset'] = [{'id': node.id}]
            response['dataset_len'] = 1
            response['success'] = True

        return response

    @action(renderer='json', name='destroy',
            permission=pyramid.security.ALL_PERMISSIONS)
    def delete(self):
        raise NotImplementedError

    @action(renderer='json',
            permission=pyramid.security.ALL_PERMISSIONS)
    def move(self):
        raise NotImplementedError
