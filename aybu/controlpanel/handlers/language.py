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
from aybu.core.utils.exceptions import ValidationError
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
            log.debug(e)
            self.session.rollback()
            success = False
            msg = _(u'Hai raggiunto il numero massimo di lingue acquistate.')

        except Exception as e:
            self.session.rollback()
            log.error('Cannot enable requested language:')
            log.error(e)
            success = False
            msg=_(u"Errore durante la procedura di aggiunta della lingua.")

        else:
            self.session.commit()
            log.debug('Enabled: %s', language)
            name = language.locale.get_display_name().title()
            success = True
            msg = _(u'Lingua %s aggiunta con successo.' % name)

        #FIXME: reload_routing()

        return dict(success=success, msg=msg)

    @action(renderer='json')
    def disable(self):
        """
            Disable the language identified by 'lang_id'.
        """
        try:
            lang_id = int(self.request.params.get('lang_id'))

            if session['lang'].id == lang_id:
                raise ValidationError('Cannot disable current language.')

            Language.disable(self.session, lang_id)
            self.session.flush()

        except ConstraintError as e:
            self.session.rollback()
            success = False
            msg = _(u"Non è possibile rimuovere tutte le lingue")
            log.debug(e)

        except Exception as e:
            self.session.rollback()
            success = False,
            msg = _(u"Errore durante il tentativo di rimuovere la lingua.")
            log.error(e)
            log.error('Unable to remove the requested language.')

        else:
            self.session.commit()
            success = True
            msg = _(u"Lingua rimossa con successo.")
            log.debug("Language %s remove successfully", language_name)

        #reload_routing()

        return dict(success=success, msg=msg)
