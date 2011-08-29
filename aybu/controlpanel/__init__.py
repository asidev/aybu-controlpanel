#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aybu.controlpanel.util import AuthenticationPolicy
from aybu.controlpanel.util import Request
from pyramid.config import Configurator
import logging
import pyramid.security


log = logging.getLogger(__name__)


def main(global_config, **settings):

    config = Configurator(settings=settings,
                          request_factory=Request,
                          authentication_policy=AuthenticationPolicy(settings))

    config.include(add_routes)
    config.include(add_views)

    return config.make_wsgi_app()


def add_routes(config):
    """
    # Admin urls.
    map.connect("login-render", "/admin/login.html", controller="login",
                action="show")
    map.connect("login-submit", "/admin/login_submit.html", controller="login",
                action="login")
    map.connect("logout", "/admin/logout.html", controller="login",
                action="logout")

    map.connect("edit", "/admin/edit", controller="page",
                action="edit_content")
    map.connect("spellchecker", "/admin/spellchecker.html",
                controller="spellchecker", action="rpc")

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
    config.add_route('root',
                     '/admin',
                     factory='aybu.controlpanel.resources.Authenticated')


def add_views(config):

    config.add_view(route_name='root',
                    renderer='string',
                    view='aybu.controlpanel.views.homepage',
                    permission=pyramid.security.ALL_PERMISSIONS)

