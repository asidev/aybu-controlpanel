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

from aybu.core.models import Language
from aybu.core.exc import QuotaError
from pyramid_handlers import action
from . base import BaseHandler
from sqlalchemy.orm.exc import NoResultFound
import pyramid.security

__all__ = ['LanguageHandler']


class LanguageHandler(BaseHandler):

    _response = dict(success=False, msg='', dataset=[], dataset_length=0)

    @action(renderer='json',
           permission=pyramid.security.ALL_PERMISSIONS)
    def enable(self):
        """
            Enable the language identified by 'lang_id'.
        """
        try:
            def_lang = self.request.registry.settings['default_locale_name']
            def_lang = Language.get_by_lang(self.session, def_lang)
            language = Language.enable(self.session,
                                       int(self.request.params['lang_id']),
                                       def_lang.id)
            self.session.flush()

        except QuotaError as e:
            self.log.exception(e)
            self.session.rollback()
            success = False
            msg = self.request.translate(
                    'Hai raggiunto il numero massimo di lingue acquistate.')

        except Exception as e:
            self.log.exception('Cannot enable requested language: %s', e)
            self.session.rollback()
            success = False
            msg=self.request.translate(
                u"Errore durante la procedura di aggiunta della lingua.")

        else:
            self.log.debug('Enabled: %s', language)
            self.session.commit()
            name = language.locale.get_display_name().title()
            success = True
            msg = self.request.translate(
                u'Lingua %s aggiunta con successo.' % name)
            self.proxy.invalidate(language=language)

        finally:
            return dict(success=success, msg=msg)

    @action(renderer='json',
           permission=pyramid.security.ALL_PERMISSIONS)
    def disable(self):
        """
            Disable the language identified by 'lang_id'.
        """
        try:
            lang_id = int(self.request.params['lang_id'])
            language = Language.disable(self.session, lang_id)
            self.session.flush()

        except QuotaError as e:
            self.log.exception(e)
            self.session.rollback()
            success = False
            msg = self.request.translate(
                        u"Non è possibile rimuovere tutte le lingue")

        except Exception as e:
            self.session.rollback()
            success = False
            msg = self.request.translate(
                    u"Errore durante il tentativo di rimuovere la lingua.")
            self.log.exception('Unable to remove the requested language: %s', e)

        else:
            self.session.commit()
            success = True
            msg = self.request.translate(u"Lingua rimossa con successo.")
            self.log.debug("Language remove successfully.")
            self.proxy.invalidate(language=language)

        finally:
            return dict(success=success, msg=msg)

    @action(renderer='json',
           permission=pyramid.security.ALL_PERMISSIONS)
    def search(self):

        response = self._response.copy()

        try:
            id_ = self.request.params['id']
            language = Language.get(self.session, id_)
            language = language.dictify(excludes=('__class__'))

        except KeyError as e:
            self.log.exception('Not ID param in the request.')
            self.session.rollback()
            self.request.response.status = 400
            response['msg'] = self.request.translate("Missing parameter: 'id'.")

        except NoResultFound as e:
            self.log.exception('No Language: %s.', id_)
            self.session.rollback()
            self.request.response.status = 404
            response['msg'] = self.request.translate("No Language found.")

        except Exception as e:
            self.log.exception('Uknown error.')
            self.session.rollback()
            self.request.response.status = 500
            response['msg'] = str(e)

        else:
            self.session.commit()
            response['success'] = True
            response['dataset'] = [language]
            response['dataset_length'] = len(response['dataset'])
            response['msg'] = self.request.translate("Language found.")

        finally:
            return response
