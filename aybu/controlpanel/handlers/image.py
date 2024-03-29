#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright 2010-2012 Asidev s.r.l.

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

from pyramid_handlers import action
from sqlalchemy.orm.exc import NoResultFound
from aybu.core.models import Image
from . base import BaseHandler
import pyramid.security


__all__ = ['ImageHandler']


class ImageHandler(BaseHandler):

    def __init__(self, request):
        super(ImageHandler, self).__init__(request)
        self.res = dict(success=False, error=dict())

    def handle_exception(self, e, fname=''):
        self.log.exception("Error in %s", fname)
        self.session.rollback()
        self.res['success'] = False
        self.res["errors"] = dict(
                    message="Error: (%s) %s" % (type(e).__name__, str(e))
        )

    # FIXME: actions is add: change to create in calling code
    @action(renderer='json', name='add',
           permission=pyramid.security.ALL_PERMISSIONS)
    def create(self):
        try:
            name = self.request.params['name']
            up_file = self.request.POST['file']
            image = Image(source=up_file.file, name=name, session=self.session)
            self.session.flush()

        except Exception as e:
            self.handle_exception(e)

        else:
            self.session.commit()
            self.res.update(image.to_dict())
            self.res['success'] = True

        finally:
            return self.res

    @action(renderer='json',
           permission=pyramid.security.ALL_PERMISSIONS)
    def update(self):
        try:
            self.res['errors'] = dict()

            try:
                id_ = int(self.request.params['id'])
            except KeyError:
                raise NoResultFound('Missing id')

            image = Image.get(self.session, id_)
            valid = False

            if 'name' in self.request.params:
                valid = True
                name = self.request.params['name']
                if name != image.name:

                    self.log.debug("Updating name of image %d to %s", id_, name)
                    if len(name) < 1:
                        raise TypeError("Il nome non può essere vuoto")

                    image.name = name

            if 'file' in self.request.POST:
                self.log.debug("Updating file for image %s", image)
                valid = True
                image.source = self.request.POST['file'].file

            if not valid:
                raise KeyError('required')

        except KeyError as e:
            self.log.debug('Missing required params in request')
            self.res['success'] = False
            self.res['errors']['name'] = "Missing value"
            self.res['errors']['file'] = "Missing value"

        except NoResultFound as e:
            self.log.debug('Cannot found image or ID missing in params')
            self.res['success'] = False
            self.res['errors']['id'] = 'Image not found'

        except TypeError as e:
            self.log.exception('Invalid name %s' % (self.request.params['name']))
            self.res['success'] = False
            self.res['errors']['name'] = str(e)

        except Exception as e:
            self.res['errors']['file'] = str(e)
            self.handle_exception(e, "update")

        else:
            self.log.debug("Updating ok, committing")
            self.session.commit()
            del self.res["errors"]
            self.res['success'] = True
            self.proxy.invalidate(url=image.url)

        finally:
            return self.res

    @action(renderer='json',
           permission=pyramid.security.ALL_PERMISSIONS)
    def remove(self):
        try:
            id_ = int(self.request.params['id'])
            image = Image.get(self.session, id_)
            image.delete()

        except Exception as e:
            self.handle_exception(e)

        else:
            self.session.commit()
            self.res['success'] = True
            self.proxy.invalidate(url=image.url)

        finally:
            return self.res

    @action(renderer='json',
           permission=pyramid.security.ALL_PERMISSIONS)
    def list(self):
        self.res = {
            'data': [img.to_dict(ref_pages=True)
                     for img in Image.all(self.session)],
            'success': True,
        }
        self.res['datalen'] = len(self.res['data'])
        return self.res

    @action(renderer='/admin/imagemanager/template.mako',
           permission=pyramid.security.ALL_PERMISSIONS)
    def index(self):
        tiny = True if "tiny" in self.request.params else False
        return dict(tiny=tiny)
