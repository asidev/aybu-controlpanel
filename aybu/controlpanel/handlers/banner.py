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

from aybu.core.models import Banner
from pyramid_handlers import action
from sqlalchemy.orm.exc import NoResultFound
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
            items = [obj.to_dict()
                     for obj in Banner.all(self.session)]

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

    @action(renderer='json',
            permission=pyramid.security.ALL_PERMISSIONS)
    def update(self):

        response = self._response.copy()

        try:
            id_ = int(self.request.matchdict['id'])
            banner = Banner.get(self.session, id_)
            # FIXME: add code to update banner info.

        except KeyError as e:
            self.log.exception('Bad request.')
            self.session.rollback()
            self.request.response.status = 400
            response['success'] = False
            response['msg'] = str(e)

        except NoResultFound as e:
            self.log.exception('Cannot found banner.')
            self.session.rollback()
            self.request.response.status = 400
            response['success'] = False
            response['msg'] = str(e)

        except TypeError as e:
            self.log.exception('Invalid name')
            self.request.response.status = 400
            response['success'] = False
            response['msg'] = str(e)

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
            response['msg'] = self.request.translate("Banner was updated.")
            self.proxy.invalidate(url=banner.url)

        finally:
            return response

    @action(renderer='json',
            permission=pyramid.security.ALL_PERMISSIONS)
    def delete(self):

        response = self._response.copy()

        try:
            banner = Banner.get(self.session, int(self.request.matchdict['id']))
            banner.delete()

        except (KeyError, ValueError, NoResultFound) as e:
            self.log.exception('Cannot get the banner to delete.')
            self.session.rollback()
            self.request.response.status = 400
            response['success'] = False
            response['msg'] = str(e)

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
            response['msg'] = self.request.translate("Banner was deleted.")
            self.proxy.invalidate(url=banner.url)

        finally:
            return response
