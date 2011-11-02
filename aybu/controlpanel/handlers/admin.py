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

import pyramid.security
from pyramid_handlers import action
from aybu.core.models import (Language,
                              PageInfo,
                              Page,
                              Banner,
                              User,
                              Logo,
                              Setting)
from aybu.core.utils.modifiers import urlify
from . base import BaseHandler


__all__ = ['AdminHandler']


class AdminHandler(BaseHandler):

    def __init__(self, request):
        super(AdminHandler, self).__init__(request)
        # FIXME: removeme
        self.request.template_helper.node = self.session.query(Page).first()

    @action(renderer='/admin/index.mako',
            permission=pyramid.security.ALL_PERMISSIONS)
    def index(self):
        return dict(page='index')

    @action(renderer='/admin/languages.mako',
            permission=pyramid.security.ALL_PERMISSIONS)
    def languages(self):
        return dict(page='languages', languages=Language.all(self.session))

    @action(renderer='/admin/password.mako',
            permission=pyramid.security.ALL_PERMISSIONS)
    def password(self):
        res = dict(page='password', success=True,
                    result_message=None, errors=dict(old_password='',
                                                     repeat_password=''))

        if not self.request.params.get('submit'):
           return res

        res['success'] = False
        try:
            User.check(self.request.session,
                       self.request.username,
                       self.request.params['old_password'])
        except ValueError:
            msg = self.request.translate(u'Vecchia password non corretta')
            res['errors']['old_password'] = msg

        new = self.request.params.get('new_password', '')
        rep = self.request.params.get('repeat_password', '')
        if new != rep:
            msg = self.request.translate(u'Le password non coincidono')
            res['errors']['repeat_password'] = msg

        elif len(new) < 6:
            msg = u'La password deve essere di almeno 6 caratteri'
            msg = self.request.translate(msg)
            res['errors']['repeat_password'] = msg

        else:
            self.request.user.password = new
            self.session.commit()
            res['success'] = True
            msg = self.request.translate(u'Password aggiornata')
            res['result_message'] = msg

        return res

    @action(renderer='/admin/images.mako',
            permission=pyramid.security.ALL_PERMISSIONS)
    def images(self):
        tiny = True if "tiny" in self.request.params else False
        return dict(page='images', tiny=tiny)

    @action(renderer='/admin/files.mako',
            permission=pyramid.security.ALL_PERMISSIONS)
    def files(self):
        tiny = True if "tiny" in self.request.params else False
        return dict(page='files', tiny=tiny)

    @action(renderer='/admin/settings.mako',
            permission=pyramid.security.ALL_PERMISSIONS)
    def settings(self):
        return dict(page='settings')

    @action(renderer='/admin/structure.mako',
            permission=pyramid.security.ALL_PERMISSIONS)
    def structure(self):
        return dict(page='structure')

    @action(renderer='json',
            permission=pyramid.security.ALL_PERMISSIONS)
    def page_banners(self):
        res = dict(success=False)
        try:
            name = self.request.params['name']
            id_ = self.request.params['nodeinfo_id']
            source = self.request.params['file']
            info = PageInfo.get(self.session, id_)
            self.log.debug("Updating banner for page '{}'".format(info.label))
            for banner in info.page.banners:
                banner.delete()
            info.page.banners = []

            info.page.banners.append(
                Banner(source=source.file, name=name, session=self.session)
            )
            self.session.flush()

        except Exception:
            self.session.rollback()
            message = u"Errore nella rimozione del banner"
            res['success'] = False
            res['error'] = self.request.translate(message)
            self.log.exception("Error removing banner")

        else:
            self.session.commit()
            # TODO: flush cache for page

        finally:
            return res

    @action(renderer='json',
            permission=pyramid.security.ALL_PERMISSIONS)
    def remove_page_banners(self):
        res = dict(success=False)
        try:
            info = PageInfo.get(self.session,
                                self.request.params['nodeinfo_id'])
            for banner in info.page.banners:
                banner.delete()

            self.session.flush()

        except Exception:
            self.session.rollback()
            message = u"Errore nella rimozione del banner"
            res['success'] = False
            res['error'] = self.request.translate(message)
            self.log.exception("Error removing banner")

        else:
            self.session.commit()
            # TODO: flush cache for page

        finally:
            return res

    @action(renderer='/admin/banner_logo.mako',
            permission=pyramid.security.ALL_PERMISSIONS)
    def banner_logo(self):
        errors = dict()
        messages = dict()
        purge_all = False

        for name in ('banner', 'logo'):
            errors[name] = None
            messages[name] = None
            cls = globals()[name.title()]

            # handle delete first
            key = 'remove_{}'.format(name)
            errors[key] = None
            messages[key] = None

            if self.request.params.get(key, None):
                obj = cls.get_default(self.session)
                if obj:
                    obj.delete()
                    purge_all = True
                message = u'{} rimosso con successo'.format(name.title())
                messages[key] = self.request.translate(message)

            # handle upload
            key = '{}_image'.format(name)
            source = self.request.params.get(key, None)
            if source:
                filename = Setting.get(self.session, name).value
                try:
                    cls(name=filename, source=source.file, session=self.session)
                    message = u'{} aggiornato con successo'.format(name.title())
                    purge_all = True

                except Exception:
                    message = u"{}: errore nell'aggiornamento"\
                                    .format(name.title())

                finally:
                    messages[key] = self.request.translate(message)

            if purge_all:
                # TODO flush all pages from proxy
                pass

        return dict(page='banner_logo', errors=errors, messages=messages)

    @action(renderer='json', name="urlfy",
            permission=pyramid.security.ALL_PERMISSIONS)
    def urlify(self):
        # FIXME change action name to urlify
        res = dict()
        name = self.request.params.get('name', '')
        try:
            res['name'] = urlify(name)

        except:
            res['name'] = ''
            res['success'] = False

        else:
            res['success'] = True

        finally:
            return res
