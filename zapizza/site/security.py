from sqlalchemy.orm.exc import NoResultFound
from pyramid_sqlalchemy import Session

from ..users.models import User


def groupfinder(username, request):
    groups = []
    user = User.by_username(username)
    if user:
        groups = user.groups
    return groups
