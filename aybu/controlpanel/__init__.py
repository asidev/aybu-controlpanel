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

from aybu.core.utils.authentication import AuthenticationPolicy
from aybu.core.utils.request import Request
from aybu.core.models import Base
from pyramid.config import Configurator
from sqlalchemy import engine_from_config

import logging
import pyramid.security


log = logging.getLogger(__name__)


def main(global_config, **settings):

    engine = engine_from_config(settings, 'sqlalchemy.')
    # Set metadata for tables.
    Base.metadata.create_all(engine)
    # Set Engine in Request factory.
    # It is needed by Request objects to build Session.
    Request.set_db_engine(engine)

    config = Configurator(settings=settings,
                          request_factory=Request,
                          authentication_policy=AuthenticationPolicy(settings))

    # Initialize Babel translation dirs.
    config.add_translation_dirs('aybu.website:locale')
    config.add_translation_dirs('aybu.controlpanel:locale')

    #config.scan('aybu.website')

    config.include(aybu.website.add_subscribers)
    config.include(aybu.website.add_assets)

    config.include(aybu.website.add_routes)
    config.include(add_routes)
    config.include(aybu.website.add_views)
    config.include(add_views)

    return config.make_wsgi_app()


def add_routes(config):

    config.add_route('login-render', '/admin/login.html')
    config.add_route('login-submit', '/admin/login_submit.html')
    config.add_route('logout', '/admin/logout.html')

    config.add_route('edit', '/admin/edit')
    config.add_route('spellchecker', '/admin/spellchecker')

    config.add_route('banner_logo', '/admin/banner_logo.html')


    """
    # Admin urls.


    map.connect("images", "/admin/images/{action}.html", controller="image")
    map.connect("files", "/admin/files/{action}.html", controller="files")
    map.connect("language", "/admin/language/{action}", controller="language")
    map.connect("structure", "/admin/structure/{action}",
                controller="structure")
    map.connect("settings", "/admin/settings/{action}", controller="setting")
    map.connect("view", "/admin/view/{action}", controller="view")

    map.connect("banner_logo", "/admin/banner_logo.html", controller="admin",
                action="banner_logo", conditions=dict(method=['POST']))

    map.connect("admin", "/admin/{action}.html", controller="admin", conditions=dict(method=['GET']))
    map.connect("admin", "/admin/{action}", controller="admin", conditions=dict(method=['POST']))

    """
    config.add_route('admin',
                     '/admin',
                     factory='aybu.controlpanel.resources.Authenticated')


def add_views(config):

    config.add_view(route_name='admin',
                    renderer='string',
                    view='aybu.controlpanel.views.homepage',
                    permission=pyramid.security.ALL_PERMISSIONS)


    config.add_view(route_name='login-render',
                    renderer='/admin/login.mako',
                    view='aybu.controlpanel.views.login')
