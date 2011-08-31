#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2010 Asidev s.r.l. - www.asidev.com
"""

import logging

from aybu.website.model import Setting
from aybu.controlpanel.lib import validator as v

from aybu.controlpanel.lib.mail import Mail

from pyramid.i18n import TranslationString as _

log = logging.getLogger(__name__)


def contact(request):
    success = True
    result_message = None
    errors = {}
    vars = {}

    for att in ('name', 'surname', 'email', 'phone', 'agreement', 'message'):
        errors[att] = ''
        vars[att] = request.params.get(att, '')

        if not getattr(v, 'validate_%s' % att)(vars[att], errors, att):
            success = False

    vars['name'] = vars['name'].title()
    vars['surname'] = vars['surname'].title()

    if not v.validate_captcha(request, errors, 'captcha'):
        success = False

    # every validation is ok!
    if success:
        q = Setting.query
        q = q.filter(Setting.name.like(u'contact_dst_email_%'))
        emails = q.all()

        mail = Mail()
        mail.setSubject(u"Nuovo messaggio dal form di contatto sul sito web")

        mail.setSender(request.POST['email'])
        message = u"Nome : %s \n" % (vars['name'])
        message = u"%sCognome : %s \n" % (message, vars['surname'])
        message = u"%sTelefono : %s \n\n" % (message, vars['phone'])

        for key, value in request.params.iteritems():
            if key not in ('name', 'surname', 'email', 'phone',
                           'agreement', 'message', 'recaptcha_response_field',
                           'recaptcha_challenge_field', 'submit'):
                p = key.decode('utf8')
                message = u"%s%s : %s \n" % (message, p.title(), value)
                vars[key] = value

        message = u"%sMessaggio : \n%s\n" % (message, vars['message'])
        mail.attachTextMessage(message)

        for email in emails:

            mail.setRecipient(email.value)

            try:
                mail.send()

            except  Exception as e:
                log.exception("Errore nell'invio del messaggio. \n%s", e)
                result_message = _(u"Errore nell'invio del messaggio. " +\
                                     u"Si prega di riprovare più tardi.")
                success = False
                break

            else:
                result_message = _(u"Grazie per averci contattato. " +\
                                         u"Le risponderemo al più presto.")

    else:
        result_message = _(u"Errore nell'invio del form. "
                             "Ricontrollare i campi e riprovare.")

    return dict(success=success, result_message=result_message, vars=vars,
                errors=errors)
