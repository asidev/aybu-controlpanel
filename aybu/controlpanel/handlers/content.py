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

import json
from pyramid_handlers import action
from . base import BaseHandler
from aybu.controlpanel.libs.spellchecking import SpellChecker


class Content(BaseHandler):
    """ Implements the RPC used by tinymce spellcheck plugin """

    def create_error(self, str, level="FATAL"):
        return {
            "errstr": str,
            "errfile": "",
            "errline": None,
            "errcontext": "",
            "level": level
        }

    def create_result(self, id=None, result=None, error=None):
        res = {"result": result, "id": id}
        if isinstance(error, basestring):
            res['error'] = self.create_error(error)
        else:
            res['error'] = error
        self.log.debug("res: %s", res)
        return res

    @action(renderer='json')
    def edit(self):
        raise NotImplementedError

    @action(renderer='json')
    def spellcheck(self):
        try:
            q = json.loads(self.request.body)
            id = q["id"]
            method = q['method']
            params = q['params']
            lang = params[0]
            words = params[1]

            checker = SpellChecker(lang)
            spell_result = getattr(checker, method)(words)
            return self.create_result(id=id, result=spell_result)

        except KeyError:
            return self.create_result(error="Could not get raw post data.")

        except Exception as e:
            return self.create_result(error=str(e))
