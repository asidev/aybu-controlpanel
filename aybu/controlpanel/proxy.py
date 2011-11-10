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

from aybu.core.models import Setting
import logging

__all__ = [ 'Proxy' ]


class Proxy(object):
    """ Factory class that returns the real proxy """

    def __new__(cls, request):
        if not Setting.get(request.db_session, 'proxy_enabled').value:
            return DummyProxy(request)

        return HttpCachePurgerProxy(request)


class BaseProxy(object):
    def __init__(self, request):
        session = request.db_session
        self._log = logging.getLogger("{}.{}".format(__name__,
                                                    self.__class__.__name__))
        self.hostname = request.host.split(":")[0]
        self.default_path = request.path_info
        self.address = Setting.get(session, 'proxy_address')
        self.port = Setting.get(session, 'proxy_port')
        self.timeout = Setting.get(session, 'proxy_purge_timeout')

    def _sanitize_path(self, paths):
        if paths is None:
            paths = [self.default_path]
        elif isinstance(paths, basestring):
            paths = [paths]
        return paths

    def ban(self, paths):
        raise NotImplementedError

    def purge(self, paths):
        raise NotImplementedError


class DummyProxy(BaseProxy):
    """ A do-nothing-proxy """

    def __init__(self, request):
        pass

    def ban(self, paths):
        return

    def purge(self, paths):
        return


class HttpCachePurgerProxy(BaseProxy):
    """ A real-world proxy that uses httpcachepurger to
        purge urls from proxy """

    @property
    def _purger(self):
        from httpcachepurger import HTTPCachePurger
        return HTTPCachePurger(self.hostname, self.address, self.port,
                               strict=True, timeout=self.timeout)

    def ban(self, paths=None):
        paths = self._sanitize_paths(paths)
        self._purger.purge(paths)

    def purge(self, paths=None):
        self._log.warning('{}.purge is currently implemented as a ban'\
                         .format(self.__class__.name__))
        return self.ban(paths)
