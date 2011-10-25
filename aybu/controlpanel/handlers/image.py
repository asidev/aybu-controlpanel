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

from BeautifulSoup import BeautifulSoup
from pyramid_handlers import action
from aybu.controlpanel.libs.htmlmodifier import update_img_src
from aybu.core.models import (Image,
                              Setting)
from . base import BaseHandler


__all__ = ['ImageHandler']


class ImageHandler(BaseHandler):

    def __init__(self, request):
        super(ImageHandler, self).__init__(request)
        self.res = dict(success=True, error=dict())

    def handle_exception(self, e, fname=''):
        self.log.exception("Error in %s", fname)
        self.session.rollback()
        self.res['success'] = False
        self.res["error"] = dict(
                    message="Error: (%s) %s" % (type(e).__name__, str(e))
        )

    # FIXME: actions is add: change to create in calling code
    @action(renderer='json', name='add')
    def create(self):
        num_images = Image.count(self.session)
        max_images = Setting.get(self.session, 'max_images')
        if max_images > 0 and max_images <= num_images:
            self.res['success'] = False
            self.res["error"] = _(u"Hai raggiunto il numero "
                                  "massimo di immagini acquistate.")
            return self.res

        try:
            name = self.request.params['name']
            up_file = self.request.POST['file']
            image = Image(source=up_file.file, name=name, session=self.session)
            self.session.commit()
            # this should not be needed, but for safety we purge
            # the url in proxy anyway
            # FIXME: purge varnish :
            # aybu.cms.lib.cache.http.purge_http(image.url)

        except Exception as e:
            self.handle_exception(e)

        finally:
            return self.res

    @action(renderer='json')
    def update(self):
        try:
            id_ = int(self.request.params['id'])
            image = Image.get(self.session, id_)
            self.res['errors'] = dict()

            try:
                name = self.request.params['name']
                if name != image.name:

                    self.log.debug("Updating name of image %d to %s", id, name)
                    if len(name) < 1:
                        raise TypeError("Il nome non può essere vuoto")

                    old_name = image.name
                    image.name = name
                    self.log.debug("Updating src of img tag "
                              "on translations using the image")

                    translations = image.get_ref_pages(self.session)
                    for t in translations:
                        soup = BeautifulSoup(t.html, smartQuotesTo=None)
                        soup = update_img_src(image.id, old_name, name, soup)
                        t.html = unicode(soup)

            except KeyError as e:
                # no name in request
                pass

            try:
                image.source = self.request.params['file'].file
            except AttributeError as e:
                # no new file in request
                pass

            self.session.commit()
            del self.res["errors"]
            # FIXME handle purge
            #aybu.cms.lib.cache.http.purge_http(image.url)

        except TypeError as e:
            self.res['success'] = False
            self.res['errors']['name'] = str(e)

        except Exception as e:
            self.res['errors']['file'] = str(e)
            self.handle_exception(e, "update")

        return self.res

    @action(renderer='json')
    def remove(self):
        try:
            id_ = int(self.request.params['id'])
            image = Image.get(self.session, id_)
            if len(image.get_ref_pages(self.session)) > 0:
                raise TypeError("Immagine %d in uso, "
                                "impossibile rimuoverla" % id)
            image.delete()
            self.session.commit()
            # FIXME handle purge
            #aybu.cms.lib.cache.http.purge_http(image.url)

        except Exception as e:
            self.handle_exception(e)

        return self.res

    @action(renderer='json')
    def list(self):
        count = Image.count(self.session)
        self.res = {"datalen": count}
        self.res['data'] = []
        for img in Image.all(self.session):
            d = img.to_dict(ref_pages=True)
            self.res['data'].append(d)

        return self.res

    @action(renderer='/admin/imagemanager/template.mako')
    def index(self):
        c.tiny = True if "tiny" in request.params else False
        return render("%s/%s/%s" % ("admin", "imagemanager", "template.mako"))
