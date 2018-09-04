from pyramid.httpexceptions import HTTPFound
from pyramid.view import (
    view_config,
    view_defaults
)
import colander
from deform import Form, ValidationFailure
from pyramid_sqlalchemy import Session
from ..users.models import User

"""
Schema para usuário
required é default, para não required informar drop
All permite mais de um validador por nodo
outros atributos em debug do objeto Form podem ser informadas (ex: oid)
DForm.Field é um tipo de DForm.Form
Limitação: type=email nao funciona com serialize() precisa ser text
"""


def username_validator(username):
    if User.by_username(username):
        return 'Este username já está em uso'


def validator_none(value):
    return True


def email_validator(email):
    if User.by_username(email):
        return 'Este e-mail já está em uso'


@colander.deferred
def deferred_sername_validator(node, kw):
    current_user = kw.get('current_user')
    username = kw.get('username')
    if username is None or username == current_user.username:
        return colander.Function(validator_none)
    else:
        return colander.Function(username_validator)


@colander.deferred
def deferred_email_validator(node, kw):
    current_user = kw.get('current_user')
    email = kw.get('email')
    if email is None or email == current_user.email:
        return colander.Function(validator_none)
    else:
        return colander.Function(email_validator)


class UserSchema(colander.MappingSchema):
    email = colander.SchemaNode(colander.String(),
                                name='email', missing=colander.required,
                                missing_msg='Campo obrigatório',
                                validator=deferred_email_validator,
                                title='E-mail', description='E-mail do usuário')
    # todo: criar validador para duplicacao de username
    # todo: criar validador regex para username letras e numeros
    username = colander.SchemaNode(colander.String(),
                                   name='username', missing=colander.required,
                                   missing_msg='Campo obrigatório',
                                   validator=deferred_sername_validator,
                                   title='Username', description='Username do usuário')
    # todo: propriedades adicionais nos nodos abaixo
    first_name = colander.SchemaNode(colander.String(), oid='email',
                                     name='first_name', missing=colander.required,
                                     missing_msg='Campo obrigatório',
                                     validator=colander.All(
                                         colander.Length(max=120, max_err='Informe um nome menor')),
                                     title='Primeiro Nome', description='Primeiro nome do usuário')
    last_name = colander.SchemaNode(colander.String(),
                                    name='last_name', missing=colander.required,
                                    missing_msg='Campo obrigatório',
                                    validator=colander.All(
                                        colander.Length(max=120, max_err='Informe um nome menor')),
                                    title='Último Nome', description='Último nome do usuário')


@view_defaults(permission='view')
class UserViews:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.current_user = User.by_username(request.authenticated_userid)
        self.messages = request.session.pop_flash()

    @view_config(route_name='users_list',
                 renderer='templates/list.jinja2'
                 )
    def list(self):
        return dict(users=User.list())

    @view_config(route_name='users_add', renderer='templates/add.jinja2')
    def add(self):
        return dict(add_form=self.profile_form.render())

    @view_config(route_name='users_add',
                 renderer='templates/add.jinja2',
                 request_method='POST')
    def add_handler(self):
        controls = self.request.POST.items()
        try:
            appstruct = self.profile_form.validate(controls)
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

    @view_config(route_name='users_view',
                 permission='view',
                 renderer='templates/view.jinja2')
    def view(self):
        return dict()

    @view_config(route_name='users_profile_edit',
                 renderer='templates/edit_profile.jinja2')
    def edit_profile(self):
        user_schema = UserSchema().bind(current_user=self.current_user,
                                        username=None,
                                        email=None)
        profile_form = Form(user_schema)
        edit_form = profile_form
        edit_form.set_appstruct(dict(
            email=self.context.email,
            username=self.context.username,
            password=self.context.password,
            first_name=self.context.first_name,
            last_name=self.context.last_name
        ))
        return dict(edit_form=edit_form)

    @view_config(route_name='users_profile_edit',
                 renderer='templates/edit_profile.jinja2',
                 request_method='POST')
    def edit_profile_handler(self):
        username = self.request.params['username']
        email = self.request.params['email']
        user_schema = UserSchema().bind(current_user=self.current_user,
                                        username=username,
                                        email=email)
        controls = self.request.POST.items()
        profile_form = Form(user_schema)
        try:
            appstruct = profile_form.validate(controls)
        except ValidationFailure as e:
            # Formulário não é válido
            edit_form = profile_form
            edit_form.set_appstruct(e.cstruct)
            return dict(edit_form=edit_form)

        # formulário válido então salve a resposta
        self.context.email = appstruct['email']
        self.context.username = appstruct['username']
        self.context.first_name = appstruct['first_name']
        self.context.last_name = appstruct['last_name']
        url = self.request.route_url('home')
        return HTTPFound(url)

    @view_config(route_name='users_delete')
    def delete(self):
        msg = 'Deleted: %s' % self.context.username
        self.request.session.flash('Deleted: %s' % self.context.username)
        Session.delete(self.context)
        url = self.request.route_url('users_list', _query=dict(msg=msg))
        return HTTPFound(url)
