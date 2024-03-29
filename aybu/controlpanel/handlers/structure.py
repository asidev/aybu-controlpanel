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

from aybu.core.exc import QuotaError, ConstraintError
from aybu.core.utils.modifiers import urlify
from aybu.core.models import (Language,
                              Menu,
                              Node,
                              ExternalLink,
                              InternalLink,
                              MediaCollectionPage,
                              Page,
                              Section,
                              ExternalLinkInfo,
                              InternalLinkInfo,
                              PageInfo,
                              MediaCollectionPageInfo,
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
                item = unicode('["{}","{}.html"]')
                item = item.format(translation.title.replace('"', "'"),
                                   translation.url)
                items.append(item)

            response = unicode('var tinyMCELinkList = new Array({});')
            response = response.format(', '.join(items))

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
            dict_ = translation.to_dict()
            try:
                dict_['home'] = node.home
            except:
                pass
            response['data'] = dict_
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
            if not parent:
                parent = '1'
            parent = Node.get(self.session, parent)
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
                                        head_content=head_content)

            elif type_ in ('Page', 'MediaCollectionPage'):
                # Page attributes.
                sitemap_priority = self.request.params.get('sitemap_priority')
                if not sitemap_priority:
                    sitemap_priority = 1
                sitemap_priority = int(sitemap_priority)
                view = self.request.params.get('page_type_id')
                if type_ == 'MediaCollectionPage':
                    # FIXME:
                    # add supporto to restrict some views to a specific node.
                    view = View.get_by_name(self.session,
                                            'MEDIA COLLECTION')
                    view = view[0] if view else None
                else:
                    view = View.get(self.session, view)

                if not Page.new_page_allowed:
                    raise QuotaError('New pages are not allowed.')

                content = self.request.params.get('content',
                                                  u'<h2>{}</h2>'.format(title))

                if type_ == 'Page':
                    node_cls = Page
                    nodeinfo_cls = PageInfo
                elif type_ == 'MediaCollectionPage':
                    node_cls = MediaCollectionPage
                    nodeinfo_cls = MediaCollectionPageInfo

                node = node_cls(enabled=enabled,
                                hidden=hidden,
                                parent=parent,
                                weight=weight,
                                sitemap_priority=sitemap_priority,
                                view=view)
                node_info = nodeinfo_cls(label=label,
                                         node=node,
                                         lang=language,
                                         title=title,
                                         url_part=url_part,
                                         meta_description=meta_description,
                                         head_content=head_content,
                                         content=content)

            elif type_ == 'InternalLink':

                linked_to = self.request.params.get('linked_to')
                linked_to = Page.get(self.session, linked_to)

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
            self.session.flush()
            if type_ == 'Page':
                home = self.request.params.get('home', 'off')
                home = True if home.lower() == 'on' else False
                if home:
                    Page.set_homepage(self.session, node)

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
            enabled = self.request.params.get('enabled', 'off')
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
                home = self.request.params.get('home', '')
                home = True if home.lower() == 'on' else False
                if home:
                    Page.set_homepage(self.session, node)
                view_id = int(self.request.params.get('page_type_id',
                                                      node.view.id))
                node.view = View.get(self.session, view_id)

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

        response = copy.deepcopy(self._response)

        try:
            id_ = int(self.request.params.get('id'))
            Node.remove(self.session, id_)

        except (TypeError, NoResultFound, ConstraintError) as e:
            log.exception('Bad request params.')
            self.session.rollback()
            self.request.response.status = 400
            response['success'] = False
            error = str(e)
            if error.split(':')[0] == '0001':
                error = 'Rimozione vietata: Menu.'
            elif error.split(':')[0] == '0002':
                error = "Rimozione vietata: ultima Pagina del sito."
            elif error.split(':')[0] == '0003':
                error = 'Rimozione vietata: eliminare prima i figli.'
            elif error.split(':')[0] == '0004':
                error = "Rimozione vietata: la pagina e' riferita da altre."
            response['error'] = error

        except Exception as e:
            log.exception('Unknown Error.')
            self.session.rollback()
            self.request.response.status = 500
            response['success'] = False
            response['error'] = str(e)

        else:
            self.session.commit()
            self.request.response.status = 200
            response['error'] = ''
            response['dataset'] = []
            response['dataset_len'] = 1
            response['success'] = True

        return response

    @action(renderer='json',
            permission=pyramid.security.ALL_PERMISSIONS)
    def move(self):

        response = copy.deepcopy(self._response)

        try:
            # The ID of the node which want be moved.
            node_id = self.request.params.get('moved_node_id')
            if not node_id is None:
                node_id = int(node_id)

            # The ID of the new parent node.
            parent_id = self.request.params.get('new_parent_id')
            if not parent_id is None:
                parent_id = int(parent_id)

            # The ID of the previous node of 'node_id' in the new position.
            previous_node_id = self.request.params.get('previous_node_id')
            if previous_node_id == '':
                previous_node_id = None
            elif not previous_node_id is None:
                previous_node_id = int(previous_node_id)

            # The ID of the next node of 'node_id' in the new position.
            next_node_id = self.request.params.get('next_node_id')
            if next_node_id == '':
                next_node_id = None
            elif not next_node_id is None:
                next_node_id = int(next_node_id)

            Node.move(self.session,
                      node_id, parent_id, previous_node_id, next_node_id)

        except (TypeError, NoResultFound, ConstraintError) as e:
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
            response['dataset'] = []
            response['dataset_len'] = 1
            response['success'] = True

        return response
