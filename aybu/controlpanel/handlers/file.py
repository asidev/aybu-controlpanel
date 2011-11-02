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

from pyramid_handlers import action
from aybu.core.models import File
from . base import BaseHandler
import pyramid.security


__all__ = ['FileHandler']


class FileHandler(BaseHandler):

    def __init__(self, request):
        super(FileHandler, self).__init__(request)
        self.res = dict(success=True, error=dict())

    def handle_exception(self, e, fname=""):
        self.log.exception("Error in %s", fname)
        self.res['success'] = False
        self.res["error"] = {
            "message": "Error: (%s) %s" % (type(e).__name__, str(e))
        }
        self.session.rollback()

    @action(renderer='json', name='add',
           permission=pyramid.security.ALL_PERMISSIONS)
    def create(self):
        try:
            name = self.request.params['name']
            up_file = self.request.POST['file']
            obj = File(session=self.session, source=up_file.file, name=name)
            self.session.flush()

        except Exception as e:
            self.handle_exception(e)

        else:
            self.session.commit()
            self.res.update(obj.to_dict())

        finally:
            return self.res

    @action(renderer='json',
           permission=pyramid.security.ALL_PERMISSIONS)
    def delete(self):
        try:
            id_ = int(self.request.params['id'])
            obj = File.get(self.session, id_)
            obj.delete()
            self.session.flush()

        except Exception as e:
            self.handle_exception(e)

        else:
            self.session.commit()

        finally:
            return self.res

    @action(renderer='json',
           permission=pyramid.security.ALL_PERMISSIONS)
    def list(self):
        num_files = File.count(self.session)
        self.res = dict(datalen=num_files, data=[])
        for f in File.all(self.session):
            d = f.to_dict(ref_pages=True)
            self.res['data'].append(d)

        return self.res

    @action(renderer='/admin/filesmanager/template.mako',
           permission=pyramid.security.ALL_PERMISSIONS)
    def index(self):
        tiny = True if "tiny" in self.request.params else False
        return dict(tiny=tiny)
