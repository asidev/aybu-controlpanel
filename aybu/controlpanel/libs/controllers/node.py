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

import logging

from aybu.core.models import Node, Menu, Page, Setting
from aybu.core.utils.exceptions import ValidationError, ConstraintError

log = logging.getLogger(__name__)


def delete(session, node_id):
    """
        Delete a node.
    """

    try:
        node = Node.get_by_id(session, node_id)
        log.debug('Deleting %s', node)

        if isinstance(node, Menu):
            error_message = "You can't remove Menu from here"
            log.warn(error_message)
            raise ValidationError(error_message)

        if isinstance(node, Page) and Page.is_last_page(session):
            error_message = "Cannot remove last page"
            log.warn(error_message)
            raise ConstraintError(error_message)

        old_weight = node.weight

        # set the node weight to a very high value so that it is "out" of
        # the tree
        node.weight = 696969
        session.flush()

        brothers_q = session.query(Node).filter(Node.parent == node.parent).\
                             filter(Node.id != node.id)

        children_q = session.query(Node).filter(Node.parent == node)

        num_children = children_q.count()
        num_brothers = brothers_q.count()

        log.debug("Num children %d", num_children)
        log.debug("Num brothers %d", num_brothers)

        log.debug("Making room for children nodes of the node to delete")
        # Update weight for those "brothers" of the node we are about to delete
        # in order to make room for its children to avoid duplicated weight
        # entries for the same parent
        brothers_q.filter(Node.weight > old_weight).update(
            values={Node.weight: Node.weight + num_children + num_brothers}
        )
        session.flush()

        log.debug("Moving old children")
        # Relocate node children up one level, adjusting their weight so they
        # take over to their father position

        children_q.update(values={
            Node.weight: old_weight + Node.weight - 1,
            Node.parent_id: node.parent_id
        })

        log.debug("Compacting nodes")
        # Move back node's brothers to compact node weights
        brothers_q.filter(Node.weight > old_weight + num_children - 1).\
                update(values={Node.weight: Node.weight - (num_brothers + 1)})
        session.flush()

        # TODO calculate and check new URLs of children

        # Due to db cascading this code should not be needed
        #for translation in node.translations:
        #    session.delete(translation)

        log.debug("Deleting node")
        session.delete(node)

        session.commit()

        # TODO FLUSH CACHE (at least varnish)

    except Exception as e:
        log.exception(e)
        session.rollback()
        raise e


def _sanitize_menu(session):
    max_menus_setting = session.query(Setting).\
                        filter(Setting.name==u'max_menus').one()

    if max_menus_setting.value < 1:
        max_menus_setting.value = 1

    max_menus = max_menus_setting.value

    log.debug('Total number of menus required by template is %d', max_menus)

    menus = session.query(Menu).order_by(Menu.weight).all()
    num_menus = len(menus)

    if num_menus > max_menus:
        log.debug('Some menus have to be removed. '
                  'Their children will be reallocated as hidden pages.')

        for i in xrange(max_menus, num_menus):
            log.debug('Removing menu number %d' % (menus[i].weight))

            while len(menus[i].children) > 0:
                # A bulk updated is more efficient but move is NEEDED because
                # this function make all needed controls
                log.debug('Moving child with id %d in menu number %d',
                          menus[i].children[0].id, menus[max_menus-1].weight)
                move(session, menus[i].children[0].id, menus[max_menus-1].id)

            session.delete(menus[i])
            menus.pop(i)
    elif num_menus < max_menus:
        for i in xrange(num_menus, max_menus):
            log.debug('Creating missing menu number %d' % (i+1))
            menu = Menu(parent=None, weight = i + 1)
            session.add(menu)
            menus.insert(i, menu)

    return menus


def _create_structure(session, lang, recurse=False):
    structure = []

    menus = _sanitize_menu(session)
    for menu in menus:
        elem = _get_item_info(session, menu, lang, recurse)
        structure.append(elem)

    return structure


def _get_item_info(session, node, lang, recurse=False):

    node_info = node.get_translation(session, lang)

    elem = {}
    elem['id'] = node.id
    elem['home'] = False
    elem['button_label'] = node_info.label
    elem['type'] = node.type
    elem['iconCls'] = node.type
    elem['enabled'] = node.enabled
    elem['hidden'] = node.hidden
    elem['checked'] = False
    elem['allowChildren'] = True
    elem['leaf'] = True
    elem['expanded'] = False
    elem['children'] = []

    if node.type in ('Menu'):
        elem['iconCls'] = 'folder'
        elem['title'] = '---'
        elem['url'] = lang.lang

    if node.type in ('Page', 'Section'):
        elem['title'] = node_info.title
        elem['url'] = node_info.url_part

    if node.type in ('Page'):
        elem['home'] = node.home

    if node.type in ('ExternalLink', 'InternalLink'):
        elem['title'] = "---"
        elem['allowChildren'] = False

    if node.type in ('ExternalLink'):
        elem['url'] = node_info.ext_url

    if node.type in ('InternalLink'):
        elem['url'] = node.linked_to.get_translation(session, lang).url

    if node.children:
        elem['leaf'] = False
        elem['expanded'] = True
        if recurse:
            for child in node.children:
                elem['children'].append(_get_item_info(session, child, lang,
                                                       recurse))

    return elem


def move(session, node_id, new_parent_id, previous_node_id=None):
    """
        Move a node
    """
    try:
        node = Node.get_by_id(session, node_id)
        old_parent = node.parent

        new_parent = Node.get_by_id(session, new_parent_id)

        if isinstance(node, Menu):
            error_message = "Root nodes can not be moved"
            log.warn(error_message)
            raise ValidationError(error_message)

        log.debug("Node to move has id %d, "
                  "had parent with id %d and had weight %d",
                  node.id, old_parent.id, node.weight)
        log.debug('New parent will be %s', new_parent)

        # get siblings in destination tree so that we can compute weights
        try:
            previous_node = Node.get_by_id(session, previous_node_id)
        except Exception as e:
            log.debug('Node is moving %s has no previous sibling', node)
            previous_node = None

        # compute weight
        if (not previous_node is None):

            if new_parent == old_parent and \
               previous_node.weight + 1 == node.weight:
                # The node was not moved
                log.debug('The node was not moved')
                return dict(success=True)

            new_weight = previous_node.weight + 1

        else:
            new_weight = 1

        log.debug('New weight will be %d', new_weight)

        # Setting node weight to an high number to avoid collisions
        old_weight = node.weight
        node.weight = 696969
        session.flush()

        # Reordering old brothers
        brothers_q = session.query(Node).filter(Node.parent == node.parent).\
                                   filter(Node.id != node.id)
        heavy_bros = brothers_q.filter(Node.weight > old_weight)
        num_heavy_bros = heavy_bros.count()

        # Augment their weight first
        heavy_bros.update(
            values={Node.weight: Node.weight + num_heavy_bros}
        )
        # Flush db to inform db of new weights
        session.flush()
        # Move back to compact node weights
        heavy_bros.update(
            values={Node.weight: Node.weight - (num_heavy_bros + 1)}
        )

        # Reordering new brothers
        brothers_q = session.query(Node).filter(Node.parent == new_parent).\
                                filter(Node.id != node.id)
        heavy_bros = brothers_q.filter(Node.weight >= new_weight)
        num_heavy_bros = heavy_bros.count()

        # augment their weight first
        heavy_bros.update(
            values={Node.weight: Node.weight + (num_heavy_bros + 1)}
        )
        # flush db to inform db of new weights
        session.flush()
        # move back to compact node weights
        heavy_bros.update(
            values={Node.weight: Node.weight - (num_heavy_bros)}
        )

        log.debug("Moving Node with id %d to new weight %d with parent %d",
                  node.id, new_weight, new_parent.id)
        node.parent = new_parent
        node.weight = new_weight

        # TODO
        # Calculate new url and set them in NodeInfo
        # URL conflict

        session.commit()

    except ValidationError as e:
        raise e

    except Exception as e:
        session.rollback()
        log.exception("An error occured moving a node : %s", e)
        raise e
