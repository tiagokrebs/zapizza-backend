from pyramid.httpexceptions import (
    HTTPOk,
    HTTPConflict,
    HTTPNotFound,
    HTTPBadRequest
)
from pyramid.security import remember, forget
from pyramid.view import view_config
from ..users.models import User
from ..empresas.models import Empresa
from ..site.token import confirm_token
from ..site.email import send_async_templated_mail
from ..site.token import generate_token
from ..site.hashid import generate_hash
from datetime import datetime, timedelta
from pyramid_sqlalchemy import Session
from json import dumps
from re import match
import colander
from jsonschema import validate, ValidationError

# todo: verificar type error em dumps de retorno
# todo: backend retorna http redirects ou decisão fica no frontend?

@colander.deferred
def deferred_email_validator(node, kw):
    current_user = kw.get('current_user')
    email = kw.get('email')
    if email is None or email == current_user.email:
        return colander.Email(msg='E-mail inválido')
    else:
        return colander.All(colander.Email(msg='Email inválido'),
                            colander.Function(email_validator))


@colander.deferred
def deferred_username_validator(node, kw):
    current_user = kw.get('current_user')
    username = kw.get('username')
    if username is None or username == current_user.username:
        return colander.All(colander.Regex(regex=r"^[a-zA-Z0-9]+$", msg='Informe apenas letras e números'),
                            colander.Length(min=3, max=120,
                                            min_err='informe no mínimo 3 caracteres',
                                            max_err='Informa no máximo 120 caracteres'))
    else:
        return colander.All(colander.Regex(regex=r"^[a-zA-Z0-9]+$", msg='Informe apenas letras e números'),
                            colander.Length(min=3, max=120,
                                            min_err='informe no mínimo 3 caracteres',
                                            max_err='Informa no máximo 120 caracteres'),
                            colander.Function(username_validator))


def email_validator(email):
    if User.by_email(email):
        return 'Este e-mail já está em uso'
    else:
        True


def username_validator(username):
    if User.by_username(username):
        return 'Este username já está em uso'
    else:
        return True


class UserSchema(colander.MappingSchema):
    email = colander.SchemaNode(colander.String(),
                                name='email', missing=colander.required,
                                missing_msg='Campo obrigatório',
                                validator=deferred_email_validator,
                                title='E-mail', description='E-mail do usuário')
    username = colander.SchemaNode(colander.String(),
                                   name='username', missing=colander.required,
                                   missing_msg='Campo obrigatório',
                                   validator=deferred_username_validator,
                                   title='Username', description='Username do usuário')
    first_name = colander.SchemaNode(colander.String(),
                                     name='firstName', missing=colander.required,
                                     missing_msg='Campo obrigatório',
                                     validator=colander.All(colander.Regex(regex=r"^[a-zA-Z]+$",
                                                                           msg='Informe apenas o primeiro nome'),
                                                            colander.Length(min=3, max=120,
                                                                            min_err='informe no mínimo 3 caracteres',
                                                                            max_err='Informa no máximo 120 caracteres')),
                                     title='Primeiro nome', description='Primeiro nome do usuário')
    last_name = colander.SchemaNode(colander.String(),
                                    name='lastName', missing=colander.required,
                                    missing_msg='Campo obrigatório',
                                    validator=colander.All(colander.Regex(regex=r"^[a-zA-Z]+$",
                                                                          msg='Informe apenas o último nome'),
                                                           colander.Length(min=3, max=120,
                                                                           min_err='informe no mínimo 3 caracteres',
                                                                           max_err='Informa no máximo 120 caracteres')),
                                    title='Último nome', description='Último nome do usuário')


class UserViews:
    def __init__(self, context, request):
        self.current_user = request.user
        self.context = context
        self.request = request

    @view_config(route_name='api_authenticated', renderer='json',
                 request_method='GET')
    def authenticated(self):
        user = self.current_user
        request = self.request
        if user:
            headers = remember(request, user.username)
            msg = 'Login efetuado com sucesso'
            token_data = {'aud': 'idToken', 'username': user.username}
            token = generate_token(request=self.request, data=token_data)
            if user.register_confirm:
                confirmed = True
            else:
                confirmed = False
            res = dumps(dict(
                data=dict(
                    code=200,
                    message=msg,
                    userId=user.username,
                    idToken=token.decode('utf-8'),
                    expiresIn=3600,
                    emailConfirmed=confirmed,
                    firstName=user.first_name,
                    lastName=user.last_name)),
                ensure_ascii=False)
            return HTTPOk(headers=headers, body=res, content_type='application/json; charset=UTF-8')

        msg = 'Falha na autenticação'
        res = dumps(dict(error=dict(code=409, message=msg)), ensure_ascii=False)
        return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='api_confirm', permission='super',
                 renderer='json', request_method='POST')
    def confirm(self):
        json_body = self.request.json_body
        if 'token' not in json_body:
            msg = 'Token não informado'
            res = dumps(dict(error=dict(code=409, message=msg)), ensure_ascii=False)
            return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')
        token = json_body['token']
        token_data = confirm_token(request=self.request, token=token, audience='registro')
        if token_data:
            aud = token_data['aud']
            email = token_data['email']
            user = User.by_email(email)
            if self.current_user and aud == 'registro' and self.current_user.email == user.email:
                # usuário já registrado direcionado para home
                if self.current_user.register_confirm:
                    msg = 'Usuário já está confirmado'
                    res = dumps(dict(data=dict(code=200, message=msg)), ensure_ascii=False)
                    return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

                # registra usuário e direciona para home
                self.current_user.register_confirm = datetime.utcnow()
                msg = 'Usuário confirmado com sucesso'
                res = dumps(dict(data=dict(code=200, message=msg)), ensure_ascii=False)
                return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

        # retorna token invalido
        msg = 'Token inválido'
        res = dumps(dict(error=dict(code=409, message=msg)), ensure_ascii=False)
        return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='api_pass_forgot', renderer='json',
                 request_method='POST')
    def pass_forgot(self):
        json_body = self.request.json_body

        schema = {
            "type": "object",
            "properties": {
                "email": {"type": "string"}
            },
            "required": ["email"]
        }
        try:
            validate(json_body, schema)
        except ValidationError as e:
            msg = e.message
            res = dumps(dict(error=dict(code=400, message=msg)), ensure_ascii=False)
            return HTTPBadRequest(body=res, content_type='application/json; charset=UTF-8')

        email = json_body['email']

        # o email precisa estar registrado
        user = User.by_email(email)
        if not user:
            msg = 'O email informado não foi encontrado'
            res = dumps(dict(error=dict(code=400, message=msg)), ensure_ascii=False)
            return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')
        else:
            # token expira em 1h, tipo registro, confirmado com email
            token_data = {'exp': datetime.utcnow() + timedelta(hours=1), 'aud': 'senha', 'email': email}
            token = generate_token(request=self.request, data=token_data)
            reset_url = self.request.registry.settings["cors.origin"] + '/reset/' + token.decode('utf-8')

            # envio de email de confirmação
            send_async_templated_mail(request=self.request, recipients=email,
                                      template='templates/email/forgot_password',
                                      context=dict(
                                          first_name=user.first_name,
                                          link=reset_url
                                      ))

            msg = 'Verifique seu email para realizar a recuperação da senha'
            res = dumps(dict(data=dict(code=200, message=msg)), ensure_ascii=False)
            return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='api_pass_reset', renderer='json',
                 request_method='POST')
    def pass_reset(self):
        json_body = self.request.json_body

        schema = {
            "type": "object",
            "properties": {
                "token": {"type": "string"},
                "password": {"type": "string"}
            },
            "required": ["token", "password"]
        }
        try:
            validate(json_body, schema)
        except ValidationError as e:
            msg = e.message
            res = dumps(dict(error=dict(code=400, message=msg)), ensure_ascii=False)
            return HTTPBadRequest(body=res, content_type='application/json; charset=UTF-8')

        token = json_body['token']
        token_data = confirm_token(request=self.request, token=token, audience='senha')
        if token_data:
            aud = token_data['aud']
            email = token_data['email']
            user = User.by_email(email)
            if user and aud == 'senha':
                password = json_body['password']
                # verifica regex mínimo para password
                if not match(r".{6,120}", password):
                    msg = 'Informe um password contendo no mínimo 6 caracteres'
                    res = dumps(dict(error=dict(code=400, message=msg)), ensure_ascii=False)
                    return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')

                user.password = password
                msg = 'Password alterado com sucesso'
                res = dumps(dict(data=dict(code=200, message=msg)), ensure_ascii=False)
                return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

        msg = 'Token inválido'
        res = dumps(dict(error=dict(code=400, message=msg)), ensure_ascii=False)
        return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='api_login', renderer='json',
                 request_method='POST')
    def login(self):
        request = self.request
        json_body = self.request.json_body

        if 'username' not in json_body:
            msg = 'Username não informado'
            res = dumps(dict(error=dict(code=409, message=msg)), ensure_ascii=False)
            return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')
        username = json_body['username']

        if 'password' not in json_body:
            msg = 'Password não informado'
            res = dumps(dict(error=dict(code=409, message=msg)), ensure_ascii=False)
            return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')
        password = json_body['password']

        user = User.by_username_email(username)
        if user and user.password == password:
            headers = remember(request, user.username)
            msg = 'Login efetuado com sucesso'
            token_data = {'aud': 'idToken', 'username': user.username}
            token = generate_token(request=self.request, data=token_data)
            if user.register_confirm:
                confirmed = True
            else:
                confirmed = False
            res = dumps(dict(
                data=dict(
                    code=200,
                    message=msg,
                    userId=user.username,
                    idToken=token.decode('utf-8'),
                    expiresIn=3600,
                    emailConfirmed=confirmed,
                    firstName=user.first_name,
                    lastName=user.last_name)),
                ensure_ascii=False)
            return HTTPOk(headers=headers, body=res, content_type='application/json; charset=UTF-8')

        msg = 'Username ou senha inválidos'
        res = dumps(dict(error=dict(code=409, message=msg)), ensure_ascii=False)
        return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='api_logout', permission='super')
    def logout(self):
        headers = forget(self.request)
        msg = 'Logout efetuado com sucesso'
        res = dumps(dict(data=dict(code=200, message=msg)), ensure_ascii=False)
        return HTTPOk(headers=headers, body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='api_signup', renderer='json',
                 request_method='POST')
    def signup(self):
        request = self.request
        json_body = self.request.json_body

        # todo: trocar validação para colander schema

        # verifica existência de email
        if 'email' not in json_body:
            msg = 'Informe um email'
            res = dumps(dict(error=dict(code=409, message=msg)), ensure_ascii=False)
            return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')
        email = json_body['email']

        # verifica uso de email por usuário existente
        if User.by_email(email):
            msg = 'O email informado já está cadastrado'
            res = dumps(dict(error=dict(code=409, message=msg)), ensure_ascii=False)
            return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')

        # verifica regex mínimo para email
        if not match(r"[^@]+@[^@]+\.[^@]+", email):
            msg = 'Informe um email válido'
            res = dumps(dict(error=dict(code=409, message=msg)), ensure_ascii=False)
            return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')

        username = email

        # verifica existência de password
        if 'password' not in json_body:
            msg = 'Informe um password'
            res = dumps(dict(error=dict(code=409, message=msg)), ensure_ascii=False)
            return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')
        password = json_body['password']

        # verifica regex mínimo para password
        if not match(r".{6,120}", password):
            msg = 'Informe um password contendo no mínimo 6 caracteres'
            res = dumps(dict(error=dict(code=409, message=msg)), ensure_ascii=False)
            return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')

        # verifica existência de firstName
        if 'firstName' not in json_body:
            msg = 'Primeiro nome não informado'
            res = dumps(dict(error=dict(code=409, message=msg)), ensure_ascii=False)
            return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')
        firstname = json_body['firstName']

        # verifica regex mínimo para firstName
        if firstname and not match(r"^[a-zA-Z]{3,120}$", firstname):
            msg = 'Primeiro nome inválido'
            res = dumps(dict(error=dict(code=409, message=msg)), ensure_ascii=False)
            return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')

        # verifica existência de lastName
        if 'lastName' not in json_body:
            msg = 'Último nome não informado'
            res = dumps(dict(error=dict(code=409, message=msg)), ensure_ascii=False)
            return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')
        lastname = json_body['lastName']

        # verifica regex mínimo para lastName
        if lastname and not match(r"^[a-zA-Z]{3,120}$", lastname):
            msg = 'Último nome inválido'
            res = dumps(dict(error=dict(code=409, message=msg)), ensure_ascii=False)
            return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')

        # insere empresa pai do usuário em registro e atualiza hash_id
        e = Empresa()
        Session.add(e)
        Session.flush()
        Session.refresh(e)
        e.hash_id = generate_hash('empresas', [e.id])

        # insere usuario em registro e atualiza hash_id
        groups = ['group:admins']
        u = User(
            email=email, username=username,
            password=password, first_name=firstname,
            last_name=lastname, groups=groups,
            empresa_id=e.id
        )
        Session.add(u)
        Session.flush()
        Session.refresh(u)
        u.hash_id = generate_hash('users', [e.id, u.id])

        # token expira em 24h, tipo registro, confirmado com email
        token_data = {'exp': datetime.utcnow() + timedelta(days=1), 'aud': 'registro', 'email': email}
        token = generate_token(request=self.request, data=token_data)
        # confirm_url = self.request.route_url('api_confirm', token=token)
        confirm_url = request.registry.settings["cors.origin"] + '/confirma/' + token.decode('utf-8')

        # envio de email de confirmação
        send_async_templated_mail(request=self.request, recipients=email,
                                  template='templates/email/confirm_register',
                                  context=dict(
                                      first_name=firstname,
                                      link=confirm_url
                                  ))

        msg = 'Verifique seu email para realizar a confirmação'
        res = dumps(dict(data=dict(code=200, message=msg)), ensure_ascii=False)
        return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='api_profile', permission='super',
                 renderer='json', request_method='GET')
    def profile_get(self):
        user = self.current_user
        if user:
            res = dumps(dict(
                data=dict(
                    code=200,
                    email=user.email,
                    username=user.username,
                    firstName=user.first_name,
                    lastName=user.last_name)),
                ensure_ascii=False)
            return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

        msg = 'Usuário não encontrado'
        res = dumps(dict(error=dict(code=404, message=msg)), ensure_ascii=False)
        return HTTPNotFound(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='api_profile', permission='super',
                 renderer='json', request_method='POST')
    def profile_post(self):
        json_body = self.request.json_body

        # montagem de cstruct elimina necessiade de validação da estrutura do json
        # objetos faltantes retornam colander.null
        cstruct = UserSchema().serialize(json_body)

        # os tipos e dados do json precisam ser validados
        # bind disponibiliza atributos dentro do contexto do schema para validações deferred
        user_schema = UserSchema().bind(current_user=self.current_user,
                                        username=cstruct['username'],
                                        email=cstruct['email'])
        try:
            appstruct = user_schema.deserialize(cstruct)
        except colander.Invalid as er:
            errors = er.asdict()

            error_list = []
            for k, v in errors.items():
                error_list.append({'field': k, 'message': v})

            msg = 'Dados inválidos'
            res = dumps(dict(
                error=dict(
                    code=400,
                    message=msg,
                    errors=error_list)),
                ensure_ascii=False)
            return HTTPBadRequest(body=res, content_type='application/json; charset=UTF-8')

        # formulario valido
        self.context.email = appstruct['email']
        self.context.first_name = appstruct['firstName']
        self.context.last_name = appstruct['lastName']

        msg = 'Sucesso'
        res = dumps(dict(
            data=dict(
                code=200,
                message=msg)),
            ensure_ascii=False)

        # alterações de username necessitam que um novo cookie seja respondido
        if appstruct['username'] != self.context.username:
            self.context.username = appstruct['username']
            headers = remember(self.request, self.context.username)
            return HTTPOk(headers=headers, body=res, content_type='application/json; charset=UTF-8')

        return HTTPOk(body=res, content_type='application/json; charset=UTF-8')
