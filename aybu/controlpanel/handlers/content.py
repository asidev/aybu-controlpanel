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
from sqlalchemy.orm.exc import NoResultFound
import pyramid.security
from aybu.core.models import PageInfo
from aybu.core.utils.spellchecking import SpellChecker

__all__ = ['ContentHandler']


class ContentHandler(BaseHandler):
    """ Implements the RPC used by the tinymce spellcheck plugin """

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

    def prepare_response(self, status, message):
        self.request.response.status_int = status
        if status == 200:
            self.session.commit()
            # TODO: purge cache

        else:
            self.session.rollback()
            self.log.debug(message)

        return self.request.translate(message)

    @action(renderer='json',
           permission=pyramid.security.ALL_PERMISSIONS)
    def edit(self):
        try:
            pageinfo = PageInfo.get(self.session,
                                    self.request.params['translation_id'])
            html = self.request.params['translation_html']
            pageinfo.content = html
            self.session.flush()

        except ValueError:
            message = self.prepare_response(status=400,
                                    message=u'Contenuto non valido')

        except KeyError:
            message = self.prepare_response(status=400,
                                    message=u'Parametri mancanti')

        except NoResultFound:
            message = self.prepare_response(status=404,
                                    message=u'Nessuna risorsa trovata')

        except Exception:
            self.log.exception('Unexpected error during content update')
            message = self.prepare_response(status=500,
                                    message=u"Errore nell'aggiornamento")

        else:
            message = self.prepare_response(status=200,
                                message=u'Contenuto aggiornato correttamente')

        finally:
            return dict(msg=message)

    @action(renderer='json',
           permission=pyramid.security.ALL_PERMISSIONS)
    def spellcheck(self):
        try:
            q = json.loads(self.request.body)
            id = q["id"]
            method = q['method']
            params = q['params']
            words = params[1]
            lang = self.request.language
            self.log.debug("Checking words %s in lang %s", words, lang)
            checker = SpellChecker(lang)

            spell_result = getattr(checker, method)(words)
            return self.create_result(id=id, result=spell_result)

        except KeyError:
            return self.create_result(error="Could not get raw post data.")

        except Exception as e:
            return self.create_result(error=str(e))
