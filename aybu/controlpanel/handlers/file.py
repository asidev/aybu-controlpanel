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
from aybu.core.models import (Setting, File)
from . base import BaseHandler


__all__ = ['FileHandler']


class FileHandler(BaseHandler):

    def __init__(self, request):
        super(FileHandler, self).__init__(request)
        self.res = dict(success=True, error=dict())

    def _handle_exception(self, e, fname=""):
        self.log.exception("Error in %s", fname)
        self.res['success'] = False
        self.res["error"] = {
            "message": "Error: (%s) %s" % (type(e).__name__, str(e))
        }
        self.session.rollback()

    @action(renderer='json', name='add')
    def create(self):
        num_files = File.count(session=self.session)
        max_files = Setting.get(self.session, 'max_files').value
        self.log.debug("Current files: %d, max: %d", num_files, max_files)
        if max_files > 0 and num_files >= max_files:
            self.res['success'] = False
            self.res["error"] = self.request.translate(
                u"Hai raggiunto il numero massimo di file acquistati.")
            return self.res

        # TODO
        # Check if disk space is reach

        try:
            name = self.request.params['name']
            up_file = self.request.POST['file']
            obj = File(session=self.session, source=up_file.file, name=name)
            self.session.flush()

        except Exception as e:
            self._handle_exception(e)

        else:
            self.session.commit()
            self.res.update(obj.to_dict())

        finally:
            return self.res

    @action(renderer='json')
    def delete(self):
        try:
            id_ = int(self.request.params['id'])
            obj = File.get(self.session, id_)
            if len(obj.get_ref_pages(self.session)) > 0:
                error = self.request.translate("File in uso, impossibile"
                                               " rimuoverlo")
                raise TypeError(error)

            obj.delete()
            self.session.flush()

        except Exception as e:
            self._handle_exception(e)

        else:
            self.session.commit()

        finally:
            return self.res

    @action(renderer='json')
    def list(self):
        num_files = File.count(self.session)
        self.res = dict(datalen=num_files, data=[])
        for f in File.all(self.session):
            d = f.to_dict(ref_pages=True)
            self.res['data'].append(d)

        return self.res

    @action(renderer='/admin/filesmanager/template.mako')
    def index(self):
        tiny = True if "tiny" in self.request.params else False
        return dict(tiny=tiny)
