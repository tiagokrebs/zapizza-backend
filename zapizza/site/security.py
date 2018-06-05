from ..users.models import User
# todo: trocar para package user

def groupfinder(username, request):
    groups = []
    user = User.by_username(username)
    if user:
        groups = user.groups
    return groups
