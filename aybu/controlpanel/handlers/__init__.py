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

from . login import LoginHandler
from . content import ContentHandler
from . image import ImageHandler
from . file import FileHandler
from . structure import StructureHandler
from . language import LanguageHandler
from . setting import SettingHandler
from . admin import AdminHandler
from . view import ViewHandler
from . pageinfo import PageInfoHandler
from . mediacollection import MediaCollectionPageHandler, MediaItemPageHandler
from . pagebanner import PageBannerHandler
from . banner import BannerHandler
from . background import BackgroundHandler

from pyramid.httpexceptions import HTTPFound

__all__ = ['LoginHandler', 'ContentHandler', 'ImageHandler', 'FileHandler',
           'StructureHandler', 'LanguageHandler', 'SettingHandler',
           'AdminHandler', 'ViewHandler', 'redirect_to_login',
           'PageInfoHandler', 'MediaCollectionPageHandler',
           'MediaItemPageHandler', 'PageBannerHandler', 'BannerHandler',
           'BackgroundHandler']


def redirect_to_login(context, request):
    """ On 403, redirect to the login page """
    request.session.flash('Effettuare il login')
    return HTTPFound(location=request.route_path('login', action='login'))
