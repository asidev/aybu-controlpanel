
from aybu.website.request import Request as BaseRequest
from aybu.website.models import Group
from aybu.website.models import User
from paste.deploy.converters import asbool
from paste.deploy.converters import asint
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authentication import AuthTktCookieHelper
from pyramid.decorator import reify
from pyramid.security import Authenticated
from pyramid.security import Everyone
from pyramid.security import forget
from pyramid.security import remember
from pyramid.security import unauthenticated_userid
from sqlalchemy.orm import joinedload


class Request(BaseRequest):

    @reify
    def user(self):
        # Query.get or session.merge are the same.
        # Using Query.get you can set earger loading options!
        userid = unauthenticated_userid(self)
        if userid is None:
            return None
        query = self.db_session.query(User).options(joinedload('groups'))
        return query.get(userid)


class AuthenticationPolicy(AuthTktAuthenticationPolicy):

    def __init__(self, settings):
        self.cookie = AuthTktCookieHelper(
            settings.get('auth.secret'),
            cookie_name=settings.get('auth.token'),
            secure=asbool(settings.get('auth.secure')),
            timeout=asint(settings.get('auth.timeout')),
            reissue_time=asint(settings.get('auth.reissue_time')),
            max_age=asint(settings.get('auth.max_age')),
            path = settings.get('auth.path'),
        )

    def authenticated_userid(self, request):
        return request.user.username if request.user else None

    def effective_principals(self, request):

        principals = [Everyone]

        if request.user:
            principals += [Authenticated, 'user:%s' % request.user.username]
            principals += ['group:%s' % g.name for g in request.user.groups]

        return principals

