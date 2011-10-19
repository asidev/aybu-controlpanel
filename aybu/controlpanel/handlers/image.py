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
                              Setting,
                              PageInfo)
from . base import BaseHandler


__all__ = ['ImageHandler']


class ImageHandler(BaseHandler):

    def __init__(self, request):
        super(ImageHandler, self).__init__(request)
        self.res = dict(success=True, error=dict())

    def handle_exception(self, e, fname=''):
        self.log.exception("Error in %s", fname)
        self.log.debug("%s: Rolling back session", fname)
        self.session.rollback()
        self.log.debug("%s: Session rolled back", fname)
        self.res['success'] = False
        self.res["error"] = dict(
                    message="Error: (%s) %s" % (type(e).__name__, str(e))
        )

    def is_used(self, id_):
        query = self.session.query(PageInfo).filter(
                        PageInfo.images.any(Image.id == id_)
                )
        return [pageinfo.id for pageinfo in query.all()]

    # FIXME: actions is add: change to create in calling code
    @action(renderer='json', name='add')
    def create(self):
        num_images = self.session.query(Image).count()
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
            img = self.session.query(Image).filter(Image.id == id_).one()
            self.res['errors'] = dict()

            try:
                name = self.request.params['name']
                if name != img.name:

                    self.log.debug("Updating name of image %d to %s", id, name)
                    if len(name) < 1:
                        raise TypeError("Il nome non può essere vuoto")

                    old_name = img.name
                    img.name = name
                    self.log.debug("Updating src of img tag "
                              "on translations using the image")

                    translations = self.session.query(PageInfo)\
                              .filter(PageInfo.images.any(Image.id == id_))\
                              .all()
                    for t in translations:
                        soup = BeautifulSoup(t.html, smartQuotesTo=None)
                        soup = update_img_src(img.id, old_name, name, soup)
                        t.html = unicode(soup)

            except KeyError as e:
                # no name in request
                pass

            try:
                # FIXME check pufferfish API
                img.update_image(self.request.params['file'].file)
            except AttributeError as e:
                pass

            self.session.commit()
            del self.res["errors"]
            # FIXME handle purge
            #aybu.cms.lib.cache.http.purge_http(img.url)

        except TypeError as e:
            self.res['success'] = False
            self.res['errors']['name'] = str(e)

        except Exception as e:
            self.res['errors']['file'] = str(e)
            self.handle_exception(e, "update")

        return self.res

    @action(renderer='json')
    def remove(self):
        # TODO
        try:
            id = int(self.request.params['id'])
            if len(self.is_used(id)) > 0:
                raise TypeError("Immagine %d in uso, "
                                "impossibile rimuoverla" % id)
            image = Image.get_by(id=id)
            image_url = image.url
            image.delete()
            self.session.commit()
            # FIXME handle purge
            #aybu.cms.lib.cache.http.purge_http(image_url)

        except Exception as e:
            self.handle_exception(e)

        return self.res

    @action(renderer='json')
    def list(self):
        # TODO
        q = Image.query
        count = q.count()
        self.res = {"datalen": count}
        self.res['data'] = []
        for img in q.all():
            d = img.to_dict()
            d['used_by'] = self.is_used(img.id)
            thumbnails = img.thumbnails
            for k in thumbnails:
                d['%s_url' % (k)] = thumbnails[k].url
            self.res['data'].append(d)

        return self.res

    @action(renderer='/admin/imagemanager/template.mako')
    def index(self):
        # TODO
        c.tiny = True if "tiny" in request.params else False
        return render("%s/%s/%s" % ("admin", "imagemanager", "template.mako"))
