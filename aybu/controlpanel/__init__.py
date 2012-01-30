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

try:
    from aybu.core.request import Request
    from aybu.core.models import Base
    import aybu.website
    from aybu.website.resources import get_root_resource
    from aybu.core.authentication import AuthenticationPolicy
    from pyramid.config import Configurator
    from pyramid_beaker import session_factory_from_settings
    from pyramid.httpexceptions import HTTPForbidden
    from sqlalchemy import engine_from_config
    import logging
    import pyramid.security
    log = logging.getLogger(__name__)
except ImportError:
    pass

__version__ = (0, 1, 0, 'dev', 0)


def main(global_config, **settings):

    engine = engine_from_config(settings, 'sqlalchemy.')
    # Set metadata for tables.
    Base.metadata.create_all(engine)
    # Set Engine in Request factory.
    # It is needed by Request objects to build Session.
    Request.set_db_engine(engine)

    session_factory = session_factory_from_settings(settings)
    auth_policy = AuthenticationPolicy()
    config = Configurator(settings=settings,
                          request_factory=Request,
                          session_factory=session_factory,
                          authentication_policy=auth_policy)

    config.include(includeme)

    # configure website
    config.include(aybu.website.includeme)

    # configure controlpanel
    return config.make_wsgi_app()


def set_session_path(request):
    request.session.path = '/admin/'


def includeme(config):
    config.add_translation_dirs('aybu.controlpanel:locale')
    config.include('pyramid_handlers')
    config.include(add_handlers)
    config.add_subscriber(
        lambda e: e.request.add_finished_callback(set_session_path),
        'pyramid.events.NewRequest')


def add_handlers(config):

    config.add_handler('MediaItemPage.delete', '/admin/mediaitempage/{id}',
                       handler='aybu.controlpanel.handlers.MediaItemPageHandler',
                       factory='aybu.core.authentication.Authenticated',
                       request_method='DELETE',
                       action='delete')

    config.add_handler('MediaItemPage.create', '/admin/mediaitempage',
                       handler='aybu.controlpanel.handlers.MediaItemPageHandler',
                       factory='aybu.core.authentication.Authenticated',
                       request_method='POST',
                       action='create')

    config.add_handler('MediaItemPage.search', '/admin/mediaitempage',
                       handler='aybu.controlpanel.handlers.MediaItemPageHandler',
                       factory='aybu.core.authentication.Authenticated',
                       request_method='GET',
                       action='search')

    config.add_handler('MediaCollectionPage.show', '/admin/mediacollectionpage/{id}',
                       handler='aybu.controlpanel.handlers.MediaCollectionPageHandler',
                       factory='aybu.core.authentication.Authenticated',
                       request_method='GET',
                       request_param="response_format=html",
                       action='show_html_view')

    config.add_handler('PageInfo.search', '/admin/PageInfo/search',
                       handler='aybu.controlpanel.handlers.PageInfoHandler',
                       factory='aybu.core.authentication.Authenticated',
                       request_method='GET',
                       action='search')

    config.add_handler('Language.search', '/admin/Language/search',
                       handler='aybu.controlpanel.handlers.LanguageHandler',
                       factory='aybu.core.authentication.Authenticated',
                       request_method='GET',
                       action='search')

    config.add_handler('login', '/admin/login.html',
                       handler='aybu.controlpanel.handlers.LoginHandler',
                       factory='aybu.core.authentication.Authenticated',
                       request_method='GET',
                       action="login")
    config.add_handler('login_post', '/admin/login.html',
                       handler='aybu.controlpanel.handlers.LoginHandler',
                       factory='aybu.core.authentication.Authenticated',
                       request_method='POST',
                       action="login")
    config.add_handler('logout', '/admin/logout',
                       handler='aybu.controlpanel.handlers.LoginHandler',
                       factory='aybu.core.authentication.Authenticated',
                       action="logout")
    config.add_handler('edit', '/admin/edit',
                       handler="aybu.controlpanel.handlers.ContentHandler",
                       factory='aybu.core.authentication.Authenticated',
                       action="edit")
    config.add_handler('spellchecker', '/admin/spellchecker.html',
                       handler="aybu.controlpanel.handlers.ContentHandler",
                       factory='aybu.core.authentication.Authenticated',
                       action="spellcheck")
    config.add_handler('images', '/admin/images/{action}.html',
                       factory='aybu.core.authentication.Authenticated',
                       handler="aybu.controlpanel.handlers.ImageHandler")
    config.add_handler('files', '/admin/files/{action}.html',
                       factory='aybu.core.authentication.Authenticated',
                       handler='aybu.controlpanel.handlers.FileHandler')
    config.add_handler('language', '/admin/language/{action}.html',
                       factory='aybu.core.authentication.Authenticated',
                       handler="aybu.controlpanel.handlers.LanguageHandler")
    config.add_handler('structure', '/admin/structure/{action}.html',
                       factory='aybu.core.authentication.Authenticated',
                       handler='aybu.controlpanel.handlers.StructureHandler')
    config.add_handler('settings', '/admin/settings/{action}',
                       factory='aybu.core.authentication.Authenticated',
                       handler='aybu.controlpanel.handlers.SettingHandler')
    config.add_handler('views', '/admin/views/{action}',
                       factory='aybu.core.authentication.Authenticated',
                       handler='aybu.controlpanel.handlers.ViewHandler')
    config.add_handler('banner_logo', '/admin/banner_logo.html',
                       handler='aybu.controlpanel.handlers.AdminHandler',
                       factory='aybu.core.authentication.Authenticated',
                       action="banner_logo", request_method='POST')
    config.add_handler('admin', '/admin/{action}.html',
                       handler='aybu.controlpanel.handlers.AdminHandler',
                       factory='aybu.core.authentication.Authenticated',
                       request_method='GET')
    config.add_handler('admin_post', '/admin/{action}',
                       handler='aybu.controlpanel.handlers.AdminHandler',
                       factory='aybu.core.authentication.Authenticated',
                       request_method='POST')

    # Put URL dispatch configuration statements before Traversal ones!!!
    config.add_route('adminpages', '/admin/*traverse',
                     factory=get_root_resource)

    config.add_view(route_name='adminpages',
                    context='aybu.core.models.NodeInfo',
                    permission=pyramid.security.ALL_PERMISSIONS,
                    view='aybu.website.views.show_page')

    config.add_view(context=HTTPForbidden,
                    view='aybu.controlpanel.handlers.redirect_to_login')
