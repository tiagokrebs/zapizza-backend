from pyramid.httpexceptions import HTTPFound
from pyramid.view import (
    view_config,
    view_defaults
)
import colander
from deform import Form, ValidationFailure
from pyramid_sqlalchemy import Session
from ..users.models import User
from ..tamanhos.models import Tamanho
from pyramid.security import remember


@view_defaults(permission='view')
class TamanhoViews:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.primary_messages = request.session.pop_flash('primary')
        self.success_messages = request.session.pop_flash('success')
        self.danger_messages = request.session.pop_flash('danger')
        self.warning_messages = request.session.pop_flash('warning')
        self.current_user = User.by_username(request.authenticated_userid)

    @view_config(route_name='tamanhos_list',
                 renderer='templates/list.jinja2'
                 )
    def list(self):
        return dict(tamanhos=Tamanho.list())