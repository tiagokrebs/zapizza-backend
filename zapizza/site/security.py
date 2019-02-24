from pyramid.security import unauthenticated_userid, Allow
from ..users.models import User


class RootFactory(object):
    __acl__ = [
        (Allow, 'group:admins', 'super'),
        (Allow, 'group:editors', 'edit'),
        (Allow, 'group:users', 'view'),
    ]

    def __init__(self, request):
        self.request = request


def groupfinder(username, request):
    groups = []
    user = request.user
    if user:
        groups = user.groups
    return groups


def get_user(request):
    userid = unauthenticated_userid(request)
    if userid is not None:
        return User.by_username_email(userid)
