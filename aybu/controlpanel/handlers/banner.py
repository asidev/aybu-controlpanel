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

from aybu.core.models import Banner
from pyramid_handlers import action
from . base import BaseHandler
import pyramid.security


__all__ = ['BannerHandler']


class BannerHandler(BaseHandler):

    _response = dict(success=False, msg='', dataset=[], dataset_length=0)

    @action(renderer='json',
            permission=pyramid.security.ALL_PERMISSIONS)
    def read(self):

        response = self._response.copy()

        try:
            items = [obj.to_dict() for obj in Banner.all(self.session)]

        except Exception as e:
            self.log.exception('Unknown error.')
            self.session.rollback()
            self.request.response.status = 500
            response['msg'] = str(e)

        else:
            response['success'] = True
            response['dataset'] = items
            response['dataset_length'] = len(response['dataset'])
            response['msg'] = self.request.translate("Banners were found.")

        finally:
            return response

    @action(renderer='json',
           permission=pyramid.security.ALL_PERMISSIONS)
    def create(self):

        response = self._response.copy()

        try:
            name = self.request.params['name']
            up_file = self.request.POST['file']
            banner = Banner(source=up_file.file, name=name, session=self.session)
            self.session.flush()

        except Exception as e:
            self.log.exception('Unknown error.')
            self.session.rollback()
            self.request.response.status = 500
            response['msg'] = str(e)

        else:
            self.session.commit()
            response['success'] = True
            response['dataset'] = [banner.to_dict()]
            response['dataset_length'] = len(response['dataset'])
            response['msg'] = self.request.translate("Banner created.")

        finally:
            return response
