from pyramid.httpexceptions import HTTPFound
from pyramid.view import (
    view_config,
    view_defaults
)
from pyramid.security import NO_PERMISSION_REQUIRED

import colander
from deform import Form, ValidationFailure

from pyramid_sqlalchemy import Session

from ..users.models import User


class UserSchema(colander.MappingSchema):
    email = colander.SchemaNode(colander.String())
    username = colander.SchemaNode(colander.String())
    password = colander.SchemaNode(colander.String())
    first_name = colander.SchemaNode(colander.String())
    last_name = colander.SchemaNode(colander.String())


class UserRegisterSchema(colander.MappingSchema):
    email = colander.SchemaNode(colander.String())
    username = colander.SchemaNode(colander.String())
    password = colander.SchemaNode(colander.String())
    confirm_password = colander.SchemaNode(colander.String())
    first_name = colander.SchemaNode(colander.String())
    last_name = colander.SchemaNode(colander.String())


@view_defaults(permission='view')
class UserViews:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.add_schema = UserSchema()
        self.register_schema = UserRegisterSchema()
        self.add_form = Form(self.add_schema, buttons=('submit',))
        self.register_form = Form(self.register_schema, buttons=('submit',))
        self.messages = request.session.pop_flash()
        self.current_user = User.by_username(request.authenticated_userid)

    @view_config(route_name='users_list',
                 renderer='templates/list.jinja2'
                 )
    def list(self):
        return dict(users=User.list())

    @view_config(route_name='users_add', renderer='templates/add.jinja2')
    def add(self):
        return dict(add_form=self.add_form.render())

    @view_config(route_name='users_add',
                 renderer='templates/add.jinja2',
                 request_method='POST')
    def add_handler(self):
        controls = self.request.POST.items()
        try:
            appstruct = self.add_form.validate(controls)
        except ValidationFailure as e:
            # Form is NOT valid
            return dict(add_form=e.render())

        # Add a new user to the database then redirect
        email = appstruct['email']
        username = appstruct['username']
        password = appstruct['password']
        first_name = appstruct['first_name']
        last_name = appstruct['last_name']
        Session.add(User(
            email=email, username=username,
            password=password, first_name=first_name,
            last_name=last_name
        ))
        user = User.by_username(username)
        self.request.session.flash('Added: %s' % user.username)
        url = self.request.route_url('users_list', id=user.username)
        return HTTPFound(url)

    @view_config(route_name='users_register',
                 renderer='templates/register.jinja2',
                 permission=NO_PERMISSION_REQUIRED)
    def register(self):
        return dict(register_form=self.register_form.render())

    @view_config(route_name='users_register',
                 renderer='templates/register.jinja2',
                 permission=NO_PERMISSION_REQUIRED,
                 request_method='POST')
    def register_handler(self):
        controls = self.request.POST.items()
        try:
            appstruct = self.register_form.validate(controls)
        except ValidationFailure as e:
            # Formulário naão é válido
            return dict(register_form=e.render())

        # Adiciona novo usuário e redireciona
        email = appstruct['email']
        username = appstruct['username']
        password = appstruct['password']
        first_name = appstruct['first_name']
        last_name = appstruct['last_name']
        groups = ['group:admins', 'group:editors']
        Session.add(User(
            email=email, username=username,
            password=password, first_name=first_name,
            last_name=last_name, groups=groups
        ))
        user = User.by_username(username)
        self.request.session.flash('Você está registrado, faça login com o seu nome de usuário ou email e senha')
        url = self.request.route_url('login', id=user.username)
        return HTTPFound(url)

    @view_config(route_name='users_view',
                 permission='view',
                 renderer='templates/view.jinja2')
    def view(self):
        return dict()

    @view_config(route_name='users_edit',
                 renderer='templates/edit.jinja2')
    def edit(self):
        edit_form = self.add_form.render(dict(
            username=self.context.username,
            password=self.context.password,
            first_name=self.context.first_name,
            last_name=self.context.last_name
        ))
        return dict(edit_form=edit_form)

    @view_config(route_name='users_edit',
                 renderer='templates/edit.jinja2',
                 request_method='POST')
    def edit_handler(self):
        controls = self.request.POST.items()
        try:
            appstruct = self.add_form.validate(controls)
        except ValidationFailure as e:
            # Form is NOT valid
            return dict(edit_form=e.render())

        # Valid form so save the data and flash message
        self.context.username = appstruct['username']
        self.context.password = appstruct['password']
        self.context.first_name = appstruct['first_name']
        self.context.last_name = appstruct['last_name']
        self.request.session.flash('Changed: %s' % self.context.username)
        url = self.request.route_url('users_view',
                                     username=self.context.username)
        return HTTPFound(url)

    @view_config(route_name='users_delete')
    def delete(self):
        msg = 'Deleted: %s' % self.context.username
        self.request.session.flash('Deleted: %s' % self.context.username)
        Session.delete(self.context)
        url = self.request.route_url('users_list', _query=dict(msg=msg))
        return HTTPFound(url)
