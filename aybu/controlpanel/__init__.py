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
import aybu.website
from pyramid.config import Configurator
from sqlalchemy import engine_from_config
import logging


log = logging.getLogger(__name__)
__version__ = (0, 1, 0, 'dev', 0)

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

    config.include(includeme)

    # configure website
    config.include(aybu.website.includeme)

    # configure controlpanel
    return config.make_wsgi_app()


def includeme(config):
    config.add_translation_dirs('aybu.controlpanel:locale')
    config.include('pyramid_handlers')
    config.include(add_handlers)


def add_handlers(config):
    """ Old mappings:

    map.connect("settings", "/admin/settings/{action}", controller="setting")

    map.connect("view", "/admin/view/{action}", controller="view")

    map.connect("banner_logo", "/admin/banner_logo.html", controller="admin",
                action="banner_logo", conditions=dict(method=['POST']))

    map.connect("admin", "/admin/{action}.html", controller="admin", conditions=dict(method=['GET']))
    map.connect("admin", "/admin/{action}", controller="admin", conditions=dict(method=['POST']))

    """

    config.add_handler('login-render', '/admin/login.html',
                       handler='aybu.controlpanel.handlers.LoginHandler',
                       action="show")
    config.add_handler('login-submit', '/admin/login_submit.html',
                       handler='aybu.controlpanel.handlers.LoginHandler',
                       action="login")
    config.add_handler('logout', '/admin/logout',
                       handler='aybu.controlpanel.handlers.LoginHandler',
                       action="logout")
    config.add_handler('edit', '/admin/edit',
                       handler="aybu.controlpanel.handlers.ContentHandler",
                       action="edit")
    config.add_handler('spellchecker', '/admin/spellchecker.html',
                       handler="aybu.controlpanel.handlers.ContentHandler",
                       action="spellcheck")
    config.add_handler('images', '/admin/images/{action}.html',
                       handler="aybu.controlpanel.handlers.ImageHandler")
    config.add_handler('files', '/admin/files/{action}.html',
                       handler='aybu.controlpanel.handlers.FileHandler')
    config.add_handler('language', '/admin/language/{action}.html',
                       handler="aybu.controlpanel.handlers.LanguageHandler")
    config.add_handler('structure', '/admin/structure/{action}.html',
                       handler='aybu.controlpanel.handlers.StructureHandler')
    config.add_handler('settings', '/admin/settings/{action}',
                       handler='aybu.controlpanel.handlers.SettingHandler')
    config.add_handler('views', '/admin/view/{action}',
                       handler='aybu.controlpanel.handlers.ViewHandler')
    config.add_handler('banner_logo', '/admin/banner_logo.html',
                       handler='aybu.controlpanel.handlers.AdminHandler',
                       action="banner_logo", request_method='POST')
    config.add_handler('admin_get', '/admin/admin/{action}.html',
                       handler='aybu.controlpanel.handlers.AdminHandler',
                       request_method='GET')
    config.add_handler('admin_post', '/admin/admin/{action}',
                       handler='aybu.controlpanel.handlers.AdminHandler',
                       request_method='POST')
