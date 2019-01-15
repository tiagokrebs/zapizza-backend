from pyramid.httpexceptions import (
    HTTPOk,
    HTTPConflict,
    HTTPBadRequest,
    HTTPForbidden,
    HTTPInternalServerError,
    HTTPNotFound
)
from pyramid.security import remember, forget
from pyramid.view import (
    view_config,
    notfound_view_config,
    forbidden_view_config,
    exception_view_config
)
from ..users.models import User
from ..empresas.models import Empresa
from ..site.token import confirm_token
from ..site.email import send_async_templated_mail
from ..site.token import generate_token
from ..site.hashid import generate_hash
from ..errors import InputError
from datetime import datetime, timedelta
from pyramid_sqlalchemy import Session
from json import dumps
from re import match
from jsonschema import validate, ValidationError


class SiteViews:
    def __init__(self, context, request):
        self.current_user = request.user
        self.context = context
        self.request = request

    @view_config(route_name='authenticated', renderer='json',
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

    @view_config(route_name='confirm', permission='super',
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

    @view_config(route_name='pass_forgot', renderer='json',
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

    @view_config(route_name='pass_reset', renderer='json',
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

    @view_config(route_name='login', renderer='json',
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

    @view_config(route_name='logout', permission='super')
    def logout(self):
        headers = forget(self.request)
        msg = 'Logout efetuado com sucesso'
        res = dumps(dict(data=dict(code=200, message=msg)), ensure_ascii=False)
        return HTTPOk(headers=headers, body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='signup', renderer='json',
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
        # confirm_url = self.request.route_url('confirm', token=token)
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

    @forbidden_view_config(renderer='json')
    def forbidden(self):
        msg = 'Forbidden'
        url = self.request.url
        res = dumps(dict(error=dict(code=403, message=msg, resource=url)), ensure_ascii=False)
        return HTTPForbidden(body=res, content_type='application/json; charset=UTF-8')

    @exception_view_config(InputError)
    def input_error(exc):
        msg = '%s' % exc.context.message
        code = exc.context.status
        res = dumps(dict(error=dict(code=code, message=msg)), ensure_ascii=False)
        return HTTPInternalServerError(body=res, content_type='application/json; charset=UTF-8')

    @exception_view_config()
    def internal_error(exc):
        msg = exc.context.args[0]
        res = dumps(dict(error=dict(code=500, message=msg)), ensure_ascii=False)
        return HTTPInternalServerError(body=res, content_type='application/json; charset=UTF-8')

    @notfound_view_config(renderer='json')
    def not_found(self):
        msg = 'Not Found'
        url = self.request.url
        res = dumps(dict(error=dict(code=404, message=msg, resource=url)), ensure_ascii=False)
        return HTTPNotFound(body=res, content_type='application/json; charset=UTF-8')
