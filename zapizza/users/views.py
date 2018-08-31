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


class UserSchema(colander.MappingSchema):
    email = colander.SchemaNode(colander.String(),
                                name='email', missing=colander.required,
                                missing_msg='Campo obrigatório',
                                validator=colander.Email('E-mail inválido'),
                                title='E-mail', description='E-mail do usuário')
    # todo: criar validador para duplicacao de username
    # todo: criar validador regex para username letras e numeros
    username = colander.SchemaNode(colander.String(),
                                   name='username', missing=colander.required,
                                   missing_msg='Campo obrigatório',
                                   validator=colander.All(
                                       colander.Length(min=3, max=120,
                                                       min_err='Informe no mínimo 3 caracteres',
                                                       max_err='Informe no máximo 120 caracteres')),
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
        self.add_schema = UserSchema()
        self.add_form = Form(self.add_schema, buttons=('submit',))
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

    @view_config(route_name='users_view',
                 permission='view',
                 renderer='templates/view.jinja2')
    def view(self):
        return dict()

    @view_config(route_name='users_edit',
                 renderer='templates/edit.jinja2')
    def edit(self):
        # children = self.add_form['email']
        # title = self.add_form['email'].title
        # value = self.add_form['email'].cstruct
        # descr = self.add_form['email'].description
        edit_form = self.add_form
        edit_form.set_appstruct(dict(
            email=self.context.email,
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
            # Formulário não é válido
            edit_form = self.add_form
            edit_form.set_appstruct(e.cstruct)
            error = edit_form['email'].errormsg
            return dict(edit_form=edit_form)

        # Valid form so save the data and flash message
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
