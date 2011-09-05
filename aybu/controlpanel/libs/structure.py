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
