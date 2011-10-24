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
from aybu.core.utils.exceptions import ConstraintError
#from aybu.core.utils.exceptions import ValidationError
from pyramid_handlers import action
from . base import BaseHandler


__all__ = ['LanguageHandler']


class LanguageHandler(BaseHandler):

    @action(renderer='json')
    def enable(self):
        """
            Enable the language identified by 'lang_id'.
        """
        try:
            language = Language.enable(self.session,
                                       int(self.request.params.get('lang_id')),
                                       int(self.request.params.get('src_clone_language_id')))
            self.session.flush()
        except ConstraintError as e:
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

        #FIXME: reload_routing()

        return dict(success=success, msg=msg)

    @action(renderer='json')
    def disable(self):
        """
            Disable the language identified by 'lang_id'.
        """
        try:
            lang_id = int(self.request.params.get('lang_id'))

            # FIXME: why this? adjust when there will be a session
            #if session['lang'].id == lang_id:
            #    raise ValidationError('Cannot disable current language.')

            Language.disable(self.session, lang_id)
            self.session.flush()

        except ConstraintError as e:
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

        # FIXME: reload_routing()

        return dict(success=success, msg=msg)
