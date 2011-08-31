#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2010 Asidev s.r.l. - www.asidev.com
"""

import logging

log = logging.getLogger(__name__)

__all__ = ["SpellChecker"]


def SpellChecker(spell_type, *a, **kw):
    log.debug("Initializing spellchecker with type=%s" % spell_type)
    if spell_type.lower() == "enchant":
        return EnchantSpellChecker(*a, **kw)
    raise TypeError("Not a valid spell checking type %s" % spell_type)


class EnchantSpellChecker(object):
    """ Spellchecker using enchant """

    def __init__(self, lang):
        import enchant
        self.lang = "%s_%s" % (lang.lang, lang.country.upper())
        self.dictionary = enchant.Dict(self.lang)

    def checkWords(self, words):
        return [word for word in words if not self.dictionary.check(word)]

    def getSuggestions(self, word):
        return self.dictionary.suggest(word)
