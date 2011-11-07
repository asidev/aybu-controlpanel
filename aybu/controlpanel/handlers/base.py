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
from pyramid.httpexceptions import HTTPBadRequest
from aybu.core.models import Language


class BaseHandler(object):
    __autoexpose__ = None

    def __init__(self, request):
        self.request = request
        self.session = self.request.db_session
        self.request.template_helper.rendering_type = 'static'
        self.request.template_helper.section = 'admin'
        self.log = logging.getLogger("%s.%s" % ( self.__class__.__module__,
                                                self.__class__.__name__))
        self.log.debug("handle request for %s", request.path_info)

        lang = request.params.get('lang')
        country = request.params.get('country')
        if bool(lang) ^ bool(country):
            # either the request contains no lang options or both.
            # if the request contains only one of the two, it's a bad request
            raise HTTPBadRequest()
        elif lang:
            self.log.debug('Setting language to %s', lang)
            request.language = Language.get_by_lang(request.db_session, lang)
