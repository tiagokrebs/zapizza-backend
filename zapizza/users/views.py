# from pyramid.httpexceptions import HTTPFound
# from pyramid.view import (
#     view_config,
#     view_defaults
# )
# import colander
# from deform import Form, ValidationFailure
# from pyramid_sqlalchemy import Session
# from ..users.models import User
# from pyramid.security import remember
#
# """
# Schema para usuário
# required é default, para não required informar drop
# All permite mais de um validador por nodo
# outros atributos em debug do objeto Form podem ser informadas (ex: oid)
# DForm.Field é um tipo de DForm.Form
# Limitação: type=email nao funciona com serialize() precisa ser text
# """
#
#
# def username_validator(username):
#     if User.by_username(username):
#         return 'Este username já está em uso'
#     else:
#         return True
#
#
# def email_validator(email):
#     if User.by_email(email):
#         return 'Este e-mail já está em uso'
#     else:
#         True
#
#
# @colander.deferred
# def deferred_username_validator(node, kw):
#     current_user = kw.get('current_user')
#     username = kw.get('username')
#     if username is None or username == current_user.username:
#         return colander.All(colander.Regex(regex=r"^[a-zA-Z0-9]+$", msg='Informe apenas letras e números'),
#                             colander.Length(min=3, max=120,
#                                             min_err='informe no mínimo 3 caracteres',
#                                             max_err='Informa no máximo 120 caracteres'))
#     else:
#         return colander.All(colander.Regex(regex=r"^[a-zA-Z0-9]+$", msg='Informe apenas letras e números'),
#                             colander.Length(min=3, max=120,
#                                             min_err='informe no mínimo 3 caracteres',
#                                             max_err='Informa no máximo 120 caracteres'),
#                             colander.Function(username_validator))
#
#
# @colander.deferred
# def deferred_email_validator(node, kw):
#     current_user = kw.get('current_user')
#     email = kw.get('email')
#     if email is None or email == current_user.email:
#         return colander.Email(msg='E-mail inválido')
#     else:
#         return colander.All(colander.Email(msg='Email inválido'),
#                             colander.Function(email_validator))
#
#
# class UserSchema(colander.MappingSchema):
#     email = colander.SchemaNode(colander.String(),
#                                 name='email', missing=colander.required,
#                                 missing_msg='Campo obrigatório',
#                                 validator=deferred_email_validator,
#                                 title='E-mail', description='E-mail do usuário')
#     username = colander.SchemaNode(colander.String(),
#                                    name='username', missing=colander.required,
#                                    missing_msg='Campo obrigatório',
#                                    validator=deferred_username_validator,
#                                    title='Username', description='Username do usuário')
#     first_name = colander.SchemaNode(colander.String(),
#                                      name='first_name', missing=colander.required,
#                                      missing_msg='Campo obrigatório',
#                                      validator=colander.All(colander.Regex(regex=r"^[a-zA-Z]+$",
#                                                                            msg='Informe apenas o primeiro nome'),
#                                                             colander.Length(min=3, max=120,
#                                                                             min_err='informe no mínimo 3 caracteres',
#                                                                             max_err='Informa no máximo 120 caracteres')),
#                                      title='Primeiro nome', description='Primeiro nome do usuário')
#     last_name = colander.SchemaNode(colander.String(),
#                                     name='last_name', missing=colander.required,
#                                     missing_msg='Campo obrigatório',
#                                     validator=colander.All(colander.Regex(regex=r"^[a-zA-Z]+$",
#                                                                           msg='Informe apenas o último nome'),
#                                                            colander.Length(min=3, max=120,
#                                                                            min_err='informe no mínimo 3 caracteres',
#                                                                            max_err='Informa no máximo 120 caracteres')),
#                                     title='Último nome', description='Último nome do usuário')
#
# # todo: rever permissoes para interação de editores com users
# # todo: 'super' deve ser apenas para register e confirm
# @view_defaults(permission='super')
# class UserViews:
#     def __init__(self, context, request):
#         self.context = context
#         self.request = request
#         self.primary_messages = request.session.pop_flash('primary')
#         self.success_messages = request.session.pop_flash('success')
#         self.danger_messages = request.session.pop_flash('danger')
#         self.warning_messages = request.session.pop_flash('warning')
#         self.current_user = User.by_username(request.authenticated_userid)
#
#     @view_config(route_name='users_list',
#                  renderer='templates/list.jinja2'
#                  )
#     def list(self):
#         return dict(users=User.list())
#
#     @view_config(route_name='users_add', renderer='templates/add.jinja2')
#     def add(self):
#         return dict(add_form=self.profile_form.render())
#
#     @view_config(route_name='users_add',
#                  renderer='templates/add.jinja2',
#                  request_method='POST')
#     def add_handler(self):
#         controls = self.request.POST.items()
#         try:
#             appstruct = self.profile_form.validate(controls)
#         except ValidationFailure as e:
#             # Form is NOT valid
#             return dict(add_form=e.render())
#
#         # Add a new user to the database then redirect
#         email = appstruct['email']
#         username = appstruct['username']
#         password = appstruct['password']
#         first_name = appstruct['first_name']
#         last_name = appstruct['last_name']
#         Session.add(User(
#             email=email, username=username,
#             password=password, first_name=first_name,
#             last_name=last_name
#         ))
#         user = User.by_username(username)
#         self.request.session.flash('Added: %s' % user.username)
#         url = self.request.route_url('users_list', id=user.username)
#         return HTTPFound(url)
#
#     @view_config(route_name='users_view',
#                  renderer='templates/view.jinja2')
#     def view(self):
#         return dict()
#
#     @view_config(route_name='users_profile_edit',
#                  renderer='templates/edit_profile.jinja2')
#     def edit_profile(self):
#         user_schema = UserSchema().bind(current_user=self.current_user,
#                                         username=None,
#                                         email=None)
#         profile_form = Form(user_schema)
#         edit_form = profile_form
#         edit_form.set_appstruct(dict(
#             email=self.context.email,
#             username=self.context.username,
#             password=self.context.password,
#             first_name=self.context.first_name,
#             last_name=self.context.last_name
#         ))
#         return dict(primary_messages=self.primary_messages,
#                     success_messages=self.success_messages,
#                     danger_messages=self.danger_messages,
#                     warning_messages=self.warning_messages,
#                     edit_form=edit_form)
#
#     @view_config(route_name='users_profile_edit',
#                  renderer='templates/edit_profile.jinja2',
#                  request_method='POST')
#     def edit_profile_handler(self):
#         username = self.request.params['username']
#         email = self.request.params['email']
#         user_schema = UserSchema().bind(current_user=self.current_user,
#                                         username=username,
#                                         email=email)
#         controls = self.request.POST.items()
#         profile_form = Form(user_schema)
#         try:
#             appstruct = profile_form.validate(controls)
#         except ValidationFailure as e:
#             # Formulário não é válido
#             edit_form = profile_form
#             edit_form.set_appstruct(e.cstruct)
#             return dict(edit_form=edit_form)
#
#         # formulario valido
#         # armazena restante dos dados
#         self.context.email = appstruct['email']
#         self.context.first_name = appstruct['first_name']
#         self.context.last_name = appstruct['last_name']
#         self.request.session.flash('Seu perfil foi atualizado', 'primary')
#
#         # lembra do novo usuario
#         if appstruct['username'] != self.context.username:
#             self.context.username = appstruct['username']
#             headers = remember(self.request, self.context.username)
#             # return HTTPFound(location=self.request.current_route_url(username=self.current_user.username),
#             #                 headers=headers)
#
#         # return HTTPFound(location=self.request.current_route_url())
#         return HTTPFound(location=self.request.route_url('home'))
#
#
#     @view_config(route_name='users_delete')
#     def delete(self):
#         msg = 'Deleted: %s' % self.context.username
#         self.request.session.flash('Deleted: %s' % self.context.username)
#         Session.delete(self.context)
#         url = self.request.route_url('users_list', _query=dict(msg=msg))
#         return HTTPFound(url)
