#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2011 Asidev s.r.l. - www.asidev.com
"""

import logging

from aybu.controlpanel.lib.exc import ConstraintException, QuotaException
from aybu.controlpanel.lib.htmlmodifier import change_href

from aybu.website.lib.common import urlify
from aybu.website.models import Node, NodeInfo, Menu, Page, Section
from aybu.website.models import InternalLink, ExternalLink, Setting
from aybu.website.models import View, Language

from sqlalchemy import desc, or_, func

log = logging.getLogger(__name__)


def check_url_part(url_part, title):
    if not url_part:
        url_part = title
    url_part = urlify(url_part)
    return url_part


def boolify(value):
    return True if value in ('on', 'ON', True, 'true', 'True', 'TRUE', 'yes',
                             'ok', 'y') else False


def is_valid_parent(parent):

    if parent is None or not isinstance(parent, (Page, Menu, Section)):
        log.warn('%s cannot have children', parent)
        return False

    return True


#def _clone_nodeinfo(nodeinfo, dst_language):
#    label = '%s [%s_%s]' % (nodeinfo.label, dst_language.lang,
#                            dst_language.country.upper())
#    title = '%s [%s_%s]' % (nodeinfo.title, dst_language.lang,
#                          dst_language.country.upper())
#
#    url_part = '%s_%s_%s' % (nodeinfo.url_part,
#                             dst_language.lang,
#                             dst_language.country.upper())
#    head_content = None
#    meta_descr = None
#    content = None
#    type_ = type(nodeinfo.node)
#
#    if type_ == Page:
#        content = '<h2>%s_%s</h2>\n%s' % (dst_language.lang,
#                                          dst_language.country.upper(),
#                                          nodeinfo.content)
#        head_content = nodeinfo.head_content
#        meta_descr = '%s [%s_%s]' % (nodeinfo.meta_description,
#                                     dst_language.lang,
#                                     dst_language.country.upper())
#    if type_ == InternalLink or type_ == ExternalLink:
#        title = None
#        url_part = None
#
#    ni = NodeInfo(title=title, label=label, url_part=url_part,
#                  content=content, lang=dst_language, images=nodeinfo.images,
#                  files=nodeinfo.files, links=nodeinfo.links,
#                  node=nodeinfo.node, head_content=head_content,
#                  meta_description=meta_descr)
#
#    dbsession.flush()
#
#    check_url(ni)


#def clone_nodeinfo(nodeinfo, src_lang):
#    q = Language.query
#    q = q.filter(Language.enabled == True)
#    q = q.filter(Language.id != src_lang.id)
#    languages = q.all()
#
#    languages = LanguagesCacheProxy()
#
#    for language in languages:
#        if src_lang.id != language.id and language.enabled:
#            _clone_nodeinfo(nodeinfo, language)
#
#
#def create_nodes_info(node, lang, label, title=None, url_part=None,
#                     meta_description=u'', head_content=u'', content=u''):
#
#    nodeinfo = NodeInfo(label=label, title=title, url_part=url_part, node=node,
#                        lang=lang, meta_description=meta_description,
#                        head_content=head_content, content=content)
#
#    dbsession.flush()
#    check_url(nodeinfo)
#
#    clone_nodeinfo(nodeinfo, lang)
#
#    return nodeinfo


def create_node(session, type_, parent=None, enabled=True, hidden=False,
                **kwargs):

    if not issubclass(type_, Node):
        raise ValueError('%s is not a Node instance' % type_)

    if not is_valid_parent(parent):
        raise ValueError('%s cannot be a parent' % parent)

    q = session.query(func.max(Node.weight)).filter(Node.parent == parent)
    try:
        #pippo = q.group_by(Node.weight).order_by(desc(Node.weight)).first()[0]
        pippo = q.group_by(Node.weight).all()

    except Exception as e:
        weight = 1

    log.info("Creating node: %s", kwargs)

    return type_(parent=parent, enabled=enabled, hidden=hidden, weight=weight,
                 **kwargs)


def create_page(session, view, parent=None, enabled=True, hidden=False,
                sitemap_priority=50, banners=[]):

    if not isinstance(view, View):
        raise ValueError('%s is not a View instance' % view)

    if not new_page_allowed(session):
        log.error('Max number of pages has been reached')
        raise QuotaException(error)

    kwargs = {'home':home, 'sitemap_priority':sitemap_priority,
              'banners':banners}

    return create_node(session, type_=Page, parent=parent, enabled=enabled,
                       hidden=hidden, home=home, banners=banners,
                       sitemap_priority=sitemap_priority)



def create_site_node(session, parametri):
    # check type (Section, Page)
    # validate_[type]
    # create_node()
    # create nodeinfo with the language of te request
    # clone nodeinfo in other languages






"""
    log.debug("create_page: %s, %s, %s, %s, %s",
              language, label, title, url_part, view)


                language, label, title, url_part,  meta_description=u'',
                head_content=u'', content=u''):
    create_nodes_info(node, lang=language, label=label, title=title,
                      url_part=url_part, meta_description=meta_description,
                      head_content=head_content, content=content)
"""


#def create_section(parent_id, language, label, title=None, url_part=None,
#                   sitemap_priority=None, enabled=True):
#
#    parent = get_parent(parent_id)
#
#    node = create_node(type_=Section, enabled=enabled,
#                       sitemap_priority=sitemap_priority, parent=parent)
#
#    create_nodes_info(node, lang=language, label=label, title=title,
#                      url_part=url_part)
#
#
#def create_internal_link(parent_id, language, label, linked_to, enabled=True):
#
#    parent = get_parent(parent_id)
#
#    node = create_node(linked_to=linked_to, type_=InternalLink,
#                       enabled=enabled, parent=parent)
#
#    create_nodes_info(node, lang=language, label=label)
#
#
#def create_external_link(parent_id, language, label, url, enabled=True):
#
#    parent = get_parent(parent_id)
#
#    node = create_node(url=url, type_=ExternalLink, enabled=enabled,
#                       parent=parent)
#
#    create_nodes_info(node, lang=language, label=label)
#
#
#def _create_page(request, lang):
#    button_label = request.params.get('button_label', None)
#    title = request.params.get('title', None)
#    meta_description = request.params.get('meta_description', None)
#    head_content = request.params.get('head_content', None)
#    sitemap_priority = request.params.get('sitemap_priority', None)
#    url_part = request.params.get('url_part', None)
#    url_part = check_url_part(url_part, title)
#    enabled = get_enabled(request)
#
#    parent_id = request.params.get('parent_id', None)
#
#    try:
#        page_type_id = int(request.params.get('page_type_id', None))
#        view = View.get_by(id=page_type_id)
#    except:
#        raise Exception('Page type does not exist')
#
#    params = dict(parent_id=parent_id, language=lang, label=button_label,
#                  title=title, url_part=url_part, view=view,
#                  content=u'<h2>%s</h2>' % (title),
#                  meta_description=meta_description,
#                  head_content=head_content,
#                  sitemap_priority=sitemap_priority,
#                  enabled=enabled)
#    log.debug("_create_page: %s", params)
#    create_page(**params)
#
#
#def _create_section(request, lang):
#    enabled = get_enabled(request)
#    button_label = request.params.get('button_label', None)
#    title = request.params.get('title', None)
#    url_part = request.params.get('url_part', None)
#    url_part = check_url_part(url_part, title)
#    sitemap_priority = request.params.get('sitemap_priority', None)
#
#    parent_id = request.params.get('parent_id', None)
#
#    create_section(parent_id=parent_id, language=lang,
#                   label=button_label, title=title, url_part=url_part,
#                   sitemap_priority=sitemap_priority,
#                   enabled=enabled)
#
#
#def _create_internallink(request, lang):
#    enabled = get_enabled(request)
#    button_label = request.params.get('button_label', None)
#    linked_to_int = int(request.params.get('linked_to', None))
#    linked_to = Node.query.filter(Node.id==linked_to_int).one()
#
#    parent_id = request.params.get('parent_id', None)
#
#    create_internal_link(parent_id=parent_id, language=lang,
#                         label=button_label, enabled=enabled,
#                         linked_to=linked_to)
#
#
#def _create_externallink(request, lang):
#    enabled = get_enabled(request)
#    button_label = request.params.get('button_label', None)
#    external_url = request.params.get('external_url', '/')
#    if not external_url.startswith("/") and not external_url.startswith("http://"):
#        external_url = "http://%s" % (external_url)
#
#    parent_id = request.params.get('parent_id', None)
#
#    create_external_link(parent_id=parent_id, language=lang,
#                         label=button_label, enabled=enabled, url=external_url)
#
#
#def create_menu_element(request, lang):
#    try:
#        type_ = request.params.get('type', None)
#
#        method_name = '_create_%s' % (type_.lower())
#
#        from aybu.cms.lib import structure
#
#        method = getattr(structure, method_name)
#
#        if callable(method):
#            method(request, lang)
#            dbsession.commit()
#            reload_routing()
#        else:
#            raise Exception('Node Type not supported')
#    except Exception as e:
#        dbsession.rollback()
#        raise e
#
#
#def destroy_node(node):
#
#    try:
#        reload = False
#        if type(node) == Page and \
#           Page.query.filter(Page.enabled == True).count() == 1:
#            error_message = "Cannot remove last page"
#            log.warn(error_message)
#            raise ConstraintException(error_message)
#        old_weight = node.weight
#
#        if type(node) == Page or type(node) == Section:
#            old_urls = _collect_old_urls(node)
#            reload = True
#
#        # set the node weight to a very high value so that it is "out" of
#        # the tree
#        node.weight = 696969
#        dbsession.flush()
#
#        brothers_q = Node.query.filter(Node.parent == node.parent).\
#                                filter(Node.id != node.id)
#        children_q = Node.query.filter(Node.parent == node)
#
#        num_children = children_q.count()
#        num_brothers = brothers_q.count()
#
#        log.debug("Num children %d", num_children)
#        log.debug("Num brothers %d", num_brothers)
#
#        log.debug("Making room for children node of the node to delete")
#        # Update weight for those "brothers" of the node we are about to delete,
#        # in order to make room for its children to avoid duplicated weight
#        # entries for the same parent
#        brothers_q.filter(Node.weight > old_weight).update(
#            values={Node.weight: Node.weight + num_children + num_brothers}
#        )
#        dbsession.flush()
#
#        log.debug("Moving old children")
#        # Relocate node children up one level, adjusting their weight so they
#        # take over to their father position
#
#        """
#        THIS QUERY SEEMS NOT WORKING USING CICLE INSTEAD
#        children_q.update(values={
#            Node.weight: old_weight + Node.weight - 1,
#            Node.parent_id: node.parent_id
#        })
#        """
#        for n in children_q.all():
#            n.weight = old_weight + Node.weight - 1
#            n.parent = node.parent
#
#        log.debug("Compacting nodes")
#        # Move back node's brothers to compact node weights
#        brothers_q.filter(Node.weight > old_weight + num_children - 1).\
#                update(values={Node.weight: Node.weight - (num_brothers + 1)})
#
#        dbsession.flush()
#
#        log.debug("Checking url and contents")
#        if reload:
#            for page in node.pages:
#                for nodeinfo in page.translations:
#                    check_url(nodeinfo)
#
#            dbsession.flush()
#            _check_contents(old_urls, node)
#
#        """
#        # Due to db cascading this code should not be needed
#        for translation in node.translations:
#            translation.delete()
#        """
#
#        log.debug("Deleting node")
#        node.delete()
#
#        dbsession.commit()
#        if reload:
#            reload_routing()
#        else:
#            aybu.cms.lib.cache.flush_all()
#
#    except Exception as e:
#        log.exception(e)
#        dbsession.rollback()
#        raise e
#
#
#def get_edit_info(node_id, lang):
#    nodeinfo = Node.query.filter(Node.id == node_id).one()[lang]
#    res = {}
#    res['id'] = nodeinfo.node.id
#    res['button_label'] = nodeinfo.label
#    res['title'] = nodeinfo.title
#    res['url_part'] = nodeinfo.url_part
#    res['meta_description'] = nodeinfo.meta_description
#    res['head_content'] = nodeinfo.head_content
#    res['enabled'] = nodeinfo.node.enabled
#
#    if type(nodeinfo.node) == Page:
#        res['page_type_id'] = nodeinfo.node.view.id
#    if type(nodeinfo.node) == InternalLink:
#        res['linked_to'] =  nodeinfo.node.linked_to.id
#    if type(nodeinfo.node) == ExternalLink:
#        res['external_url'] = nodeinfo.node.url
#
#    return res
#
#
#def _collect_old_urls(node):
#
#    log.debug("Collecting old url")
#
#    old_urls = {}
#    for page in node.pages:
#        for nodeinfo in page.translations:
#            old_urls[nodeinfo.url] = nodeinfo
#
#    log.debug("old urls collected %s", old_urls)
#
#    return old_urls
#
#
#def _check_contents(old_urls, delete_node = None):
#
#    log.debug("Replacing old url in the contents of pages having link to changed url")
#
#    cond = []
#
#    old_url_cleaned = dict(old_urls)
#    if delete_node:
#        for nodeinfo in delete_node.translations:
#            old_url_cleaned[nodeinfo.url] = None
#
#    analyzed = []
#
#    for ni in old_urls.values():
#        cond.append(NodeInfo.links.any(NodeInfo.id == ni.id))
#        q = NodeInfo.query.filter(or_(*cond))
#
#        for new_src_nodeinfo in q.all():
#            if new_src_nodeinfo not in analyzed:
#                change_href(new_src_nodeinfo, old_url_cleaned)
#                analyzed.append(new_src_nodeinfo)
#
#
#def update_node(request, lang):
#    try:
#        routing_changed = False
#        button_label = request.params.get('button_label', None)
#        title = request.params.get('title', None)
#        meta_description = request.params.get('meta_description', None)
#        head_content = request.params.get('head_content', None)
#        url_part = request.params.get('url_part', None)
#        enabled = get_enabled(request)
#
#        node_id = int(request.params.get('id', None))
#        node = Node.query.filter(Node.id == node_id).one()
#
#        # What to do if has any children?
#        node.enabled = enabled
#
#        nodeinfo = node[lang]
#        nodeinfo.title = title
#        nodeinfo.label = button_label
#        nodeinfo.meta_description = meta_description
#        nodeinfo.head_content = head_content
#
#        if type(node) == Page or type(node) == Section:
#            url_part = check_url_part(url_part, title)
#            if nodeinfo.url_part != url_part:
#                old_urls = _collect_old_urls(node)
#                routing_changed = True
#
#            nodeinfo.url_part = url_part
#
#        if type(node) == Page:
#            try:
#                page_type_id = int(request.params.get('page_type_id', None))
#                view = View.query.filter(View.id == page_type_id).one()
#                node.view = view
#            except:
#                raise Exception('Page type does not exist')
#
#        elif type(node) == InternalLink:
#            try:
#                linked_to_id = int(request.params.get('linked_to', None))
#                node.linked_to = Node.query.filter(Node.id == linked_to_id).one()
#            except:
#                raise Exception('Linked page does not exist')
#
#        elif type(node) == ExternalLink:
#            external_url = request.params.get('external_url', '/')
#            if not external_url.startswith("/") and \
#               not external_url.startswith("http://"):
#                external_url = "http://%s" % (external_url)
#                node.url = external_url
#
#        if routing_changed:
#            dbsession.flush()
#            check_url(nodeinfo)
#            _check_contents(old_urls)
#
#        dbsession.commit()
#
#        if routing_changed:
#            reload_routing()
#        else:
#            aybu.cms.lib.cache.flush_all()
#
#    except Exception as e:
#        log.exception(e)
#        dbsession.rollback()
#        raise e
#
#
#def move_node(id, parent_id, previous_node_id, next_node_id):
#
#    try:
#        nq = Node.query
#        node = nq.filter(Node.id == id).one()
#        old_parent = node.parent
#        new_parent = nq.filter(Node.id == parent_id).one()
#
#        if old_parent != new_parent:
#            old_urls = _collect_old_urls(node)
#
#        if type(node) == Menu:
#            error_message = "Root nodes can not be moved"
#            log.warn(error_message)
#            raise Exception(error_message)
#
#        if type(new_parent) not in (Menu, Page, Section):
#            error_message = "%s cannot have children", new_parent
#            log.warn(error_message)
#            raise Exception(error_message)
#
#        log.debug("Node to move has id %d, "
#                  "had parent with id %d and had weight %d",
#                  node.id, node.parent.id, node.weight)
#        log.debug('New parent will be %s', new_parent)
#
#        # get siblings in destination tree so that we can compute weights
#        try:
#            previous_node = nq.filter(Node.id == previous_node_id).one()
#        except Exception as e:
#            log.debug('Moved Node %s has no previous sibling', node)
#            previous_node = None
#
#        try:
#            next_node = nq.filter(Node.id == next_node_id).one()
#        except Exception as e:
#            log.debug('Moved Node %s has no next sibling', node)
#            next_node = None
#
#        # compute weight
#        if previous_node and next_node:
#
#            if previous_node.weight + 1 == next_node.weight - 1 and \
#                 new_parent == node.parent and \
#                 previous_node.weight + 1 == node.weight:
#                # The node was not moved
#                return dict(success=True)
#
#            new_weight = next_node.weight
#
#        elif previous_node:
#            new_weight = previous_node.weight + 1
#        elif next_node:
#            new_weight = next_node.weight - 1
#        else:
#            new_weight = 1
#
#        log.debug('New weight will be %d', new_weight)
#
#        # Setting node weight to an high number to avoid collisions
#        old_weight = node.weight
#        node.weight = 696969
#        dbsession.flush()
#
#        # Reordering old brothers
#        brothers_q = Node.query.filter(Node.parent == node.parent).\
#                                filter(Node.id != node.id)
#        heavy_bros = brothers_q.filter(Node.weight > old_weight)
#        num_heavy_bros = heavy_bros.count()
#
#        # augment their weight first
#        heavy_bros.update(
#            values={Node.weight: Node.weight + num_heavy_bros}
#        )
#        # flush db to inform db of new weights
#        dbsession.flush()
#        # move back to compact node weights
#        heavy_bros.update(
#            values={Node.weight: Node.weight - (num_heavy_bros + 1)}
#        )
#
#        # Reordering new brothers
#        brothers_q = Node.query.filter(Node.parent == new_parent).\
#                                filter(Node.id != node.id)
#        heavy_bros = brothers_q.filter(Node.weight >= new_weight)
#        num_heavy_bros = heavy_bros.count()
#
#        # augment their weight first
#        heavy_bros.update(
#            values={Node.weight: Node.weight + (num_heavy_bros + 1)}
#        )
#        # flush db to inform db of new weights
#        dbsession.flush()
#        # move back to compact node weights
#        heavy_bros.update(
#            values={Node.weight: Node.weight - (num_heavy_bros)}
#        )
#
#        log.debug("Moving Node with id %d to new weight %d with parent %d",
#                  node.id, new_weight, new_parent.id)
#        node.parent = new_parent
#        node.weight = new_weight
#
#        if old_parent != new_parent:
#            dbsession.flush()
#            for page in node.pages:
#                for nodeinfo in page.translations:
#                    check_url(nodeinfo)
#
#            _check_contents(old_urls)
#
#        dbsession.commit()
#
#        if old_parent != new_parent:
#            reload_routing()
#        else:
#            aybu.cms.lib.cache.flush_all()
#
#    except ConstraintException as e:
#        dbsession.rollback()
#        log.exception("Nodes can't share url : %s", e)
#        raise e
#
#    except Exception as e:
#        dbsession.rollback()
#        log.exception("An error occured moving a node : %s", e)
#        raise e
