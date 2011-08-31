#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import re

from pylons.i18n.translation import _

from recaptcha.client.captcha import submit

log = logging.getLogger(__name__)


def validate_email(email, errors, key):
    pattern = "[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
    compiled = re.compile(pattern)
    if not compiled.match(email):
        errors[key] = _(u"Inserisci un indirizzo email valido.")
        return False
    return True


def validate_domain_name(domain, errors, key):
    pattern = "(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
    compiled = re.compile(pattern)
    if not compiled.match(domain):
        errors[key] = _(u"Inserisci un dominio valido.")
        return False
    return True


def validate_phone(number, errors, key):
    pattern = "^(\+){0,1}([0-9-()]|( ))+$"
    compiled = re.compile(pattern)
    if not compiled.match(number):
        errors[key] = _(u"Inserisci un numero di telefono valido.")
        return False
    return True


def validate_surname(value, errors, key):
    return validate_name(value, errors, key)


def validate_name(value, errors, key):
    pattern = "[(0-9@*(\)[\]+.,/?:;\"`~\\#$%^&<>)+]"
    compiled = re.compile(pattern)
    if compiled.search(value) is None:
        if len(value) < 2:
            errors[key] = _(u"Inserisci almeno 2 caratteri.")
            return False
    else:
        errors[key] = _(u"Numeri o caratteri speciali non sono ammessi.")
        return False

    return True


def validate_message(message, errors, key):
    if len(message) < 10:
        errors[key] = _(u"Inserisci almeno 10 caratteri.")
        return False
    return True


def validate_agreement(value, errors, key):
    if not value == 'on':
        errors[key] = _(u"Devi accettare i termini di Privacy")
        return False
    return True


def validate_captcha(request, errors, key):

    private_key = '6LeNHcYSAAAAAM7o91qbVfLAFjxoj336p3LL7YZB'

    try:
        response_field = request.params.get('recaptcha_response_field', '')
        challenge_field = request.params.get('recaptcha_challenge_field', '')
        recaptcha_response = submit(challenge_field, response_field,
                                    private_key, request.remote_addr)

        if not recaptcha_response.is_valid:
            errors[key] = _(u"Il testo da lei inserito non corrisponde con quello visualizzato nell'immagine. La preghiamo di riprovare.")
            return False

    except Exception as e:
        log.exception('Error validating captcha code')
        errors[key] = _(u"Errore durante la validazione del captcha")
        return False

    return True
