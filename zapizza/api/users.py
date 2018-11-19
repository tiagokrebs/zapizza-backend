from pyramid.httpexceptions import (
    HTTPOk,
    HTTPUnauthorized,
    HTTPConflict
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


# todo: verificar type error em dumps de retorno
# todo: backend retorna http redirects ou decisão fica no frontend?

class ApiViews:
    def __init__(self, context, request):
        self.current_user = request.user
        self.context = context
        self.request = request

    @view_config(route_name='api_confirm', permission='super',
                 renderer='json', request_method='POST')
    def confirm(self):
        json_body = self.request.json_body
        if 'token' not in json_body:
            msg = 'Token não informado'
            res = dumps(dict(message=msg), ensure_ascii=False)
            return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')
        token = json_body['request.paramstoken']
        token_data = confirm_token(request=self.request, token=token, audience='registro')
        if token_data:
            aud = token_data['aud']
            email = token_data['email']
            user = User.by_email(email)
            if self.current_user and aud == 'registro' and self.current_user.email == user.email:
                # usuário já registrado direcionado para home
                if self.current_user.register_confirm:
                    msg = 'Usuário já está confirmado'
                    res = dumps(dict(message=msg), ensure_ascii=False)
                    return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

                # registra usuário e direciona para home
                self.current_user.register_confirm = datetime.utcnow()
                msg = 'Usuário confirmado com sucesso'
                res = dumps(dict(message=msg), ensure_ascii=False)
                return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

        # retorna token invalido
        msg = 'Token inválido'
        res = dumps(dict(message=msg), ensure_ascii=False)
        return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='api_password_forgot', renderer='json',
                 request_method='POST')
    def password_forgot(self):
        json_body = self.request.json_body
        if 'email' not in json_body:
            msg = 'Email não informado'
            res = dumps(dict(message=msg), ensure_ascii=False)
            return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')
        else:
            email = json_body['email']
            # verifica se o email informado existe
            if not User.by_email(email):
                msg = 'O email informado não foi encontrado'
                res = dumps(dict(message=msg), ensure_ascii=False)
                return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')
            else:
                user = User.by_email(email)
                # token expira em 1h, tipo registro, confirmado com email
                token_data = {'exp': datetime.utcnow() + timedelta(hours=1), 'aud': 'senha', 'email': email}
                token = generate_token(request=self.request, data=token_data)
                reset_url = self.request.route_url('reset', token=token)

                # envio de email de confirmação
                send_async_templated_mail(request=self.request, recipients=email,
                                          template='templates/email/forgot_password',
                                          context=dict(
                                              first_name=user.first_name,
                                              link=reset_url
                                          ))

                if user:
                    msg = 'Verifique seu email para realizar a recuperação da senha'
                    res = dumps(dict(message=msg), ensure_ascii=False)
                    return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='api_password_reset', renderer='json',
                 request_method='POST')
    def password_reset(self):
        json_body = self.request.json_body
        if 'token' not in json_body:
            msg = 'Token não informado'
            res = dumps(dict(message=msg), ensure_ascii=False)
            return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')
        token = json_body['token']
        token_data = confirm_token(request=self.request, token=token, audience='senha')
        if token_data:
            aud = token_data['aud']
            email = token_data['email']
            user = User.by_email(email)
            if user and aud == 'senha':
                # verifica existência de password
                if 'password' not in json_body:
                    msg = 'Password não informado'
                    res = dumps(dict(message=msg), ensure_ascii=False)
                    return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')
                password = json_body['password']
                # verifica regex mínimo para password
                if not match(r".{6,120}", password):
                    msg = 'Informe um passord contendo no mínimo 6 caracteres'
                    res = dumps(dict(message=msg), ensure_ascii=False)
                    return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')

                user.password = password
                msg = 'Password alterado com sucesso'
                res = dumps(dict(message=msg), ensure_ascii=False)
                return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

        msg = 'Token inválido'
        res = dumps(dict(message=msg), ensure_ascii=False)
        return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')

    # todo: utilizar Deform + Schemas para validação dos atributos ver user_edit_profile
    @view_config(route_name='reset',
                 renderer='templates/reset.jinja2',
                 request_method='POST')
    def reset_handler(self):
        """
        Ao receber confirmação da recuperação de senha valida os dados
        define password no registro do usuário e direciona para página de login
        """
        if 'form.submitted' in self.request.params:
            token = self.request.matchdict.get('token')
            token_data = confirm_token(request=self.request, token=token, audience='senha')
            if token_data:
                aud = token_data['aud']
                email = token_data['email']
                user = User.by_email(email)
                password = self.request.params['password']
                cpassword = self.request.params['cpassword']

                if user and aud == 'senha':
                    # verifica existência de password
                    if not password:
                        return dict(form_error='Informe um password')

                    # verifica regex mínimo para password
                    if not re.match(r".{6,120}", password):
                        return dict(form_error='Informe um passord contendo no mínimo 6 caracteres')

                    # verifica existência de cpassword
                    if not cpassword:
                        return dict(form_error='Informe a confirmação do password')

                    # verifia igualdadade entre passwords
                    if cpassword != password:
                        return dict(form_error='A confirmação do password incorreta')

                    # ajusta password no registro e direciona
                    # Session.query(user).filter(user.email == email). \
                    #    update({user.password: password}, synchorize_session=False)
                    user.password = password
                    url = self.request.route_url('login')
                    return HTTPFound(url)

        return dict(form_error='Token inválido')

    @view_config(route_name='api_login', renderer='json',
                 request_method='POST')
    def login(self):
        request = self.request
        json_body = self.request.json_body

        if 'username' not in json_body:
            msg = 'Username não informado'
            res = dumps(dict(message=msg), ensure_ascii=False)
            return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')
        username = json_body['username']

        if 'password' not in json_body:
            msg = 'Password não informado'
            res = dumps(dict(message=msg), ensure_ascii=False)
            return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')
        password = json_body['password']

        user = User.by_username_email(username)
        if user and user.password == password:
            headers = remember(request, user.username)
            msg = 'Login efetuado com sucesso'
            res = dumps(dict(message=msg), ensure_ascii=False)
            return HTTPOk(headers=headers, body=res, content_type='application/json; charset=UTF-8')

        msg = 'Username ou senha inválido'
        res = dumps(dict(message=msg), ensure_ascii=False)
        return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='api_logout', permission='super')
    def logout(self):
        headers = forget(self.request)
        msg = 'Logout efetuado com sucesso'
        res = dumps(dict(message=msg), ensure_ascii=False)
        return HTTPOk(headers=headers, body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='api_signup', renderer='json',
                 request_method='POST')
    def signup(self):
        json_body = self.request.json_body

        # verifica existência de email
        if 'email' not in json_body:
            msg = 'Informe um email'
            res = dumps(dict(message=msg), ensure_ascii=False)
            return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')
        email = json_body['email']

        # verifica uso de email por usuário existente
        if User.by_email(email):
            msg = 'O email informado já está cadastrado'
            res = dumps(dict(message=msg), ensure_ascii=False)
            return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')

        # verifica regex mínimo para email
        if not match(r"[^@]+@[^@]+\.[^@]+", email):
            msg = 'Informe um email válido'
            res = dumps(dict(message=msg), ensure_ascii=False)
            return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')

        # verifica existência de username
        if 'username' not in json_body:
            msg = 'Informe um username'
            res = dumps(dict(message=msg), ensure_ascii=False)
            return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')
        username = json_body['username']
        
        # verifica uso de username por usuário existente
        if User.by_username(username):
            msg = 'O username informado já está cadastrado'
            res = dumps(dict(message=msg), ensure_ascii=False)
            return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')

        # verifica regex mínimo para username
        if not match(r"^[a-zA-Z0-9]{3,120}$", username):
            msg = 'Username inválido'
            res = dumps(dict(message=msg), ensure_ascii=False)
            return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')

        # verifica existência de password
        if 'password' not in json_body:
            msg = 'Informe um password'
            res = dumps(dict(message=msg), ensure_ascii=False)
            return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')
        password = json_body['password']

        # verifica regex mínimo para password
        if not match(r".{6,120}", password):
            msg = 'Informe um password contendo no mínimo 6 caracteres'
            res = dumps(dict(message=msg), ensure_ascii=False)
            return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')

        # verifica existência de fname
        if 'fname' not in json_body:
            msg = 'Primeiro nome não informado'
            res = dumps(dict(message=msg), ensure_ascii=False)
            return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')
        fname = json_body['fname']

        # verifica regex mínimo para fname
        if fname and not match(r"^[a-zA-Z]{3,120}$", fname):
            msg = 'Primeiro nome inválido'
            res = dumps(dict(message=msg), ensure_ascii=False)
            return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')

        # verifica existência de lname
        if 'lname' not in json_body:
            msg = 'Último nome não informado'
            res = dumps(dict(message=msg), ensure_ascii=False)
            return HTTPConflict(body=res, content_type='application/json; charset=UTF-8')
        lname = json_body['lname']

        # verifica regex mínimo para lname
        if lname and not match(r"^[a-zA-Z]{3,120}$", lname):
            msg = 'Último nome inválido'
            res = dumps(dict(message=msg), ensure_ascii=False)
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
            password=password, first_name=fname,
            last_name=lname, groups=groups,
            empresa_id=e.id
        )
        Session.add(u)
        Session.flush()
        Session.refresh(u)
        u.hash_id = generate_hash('users', [e.id, u.id])

        # token expira em 24h, tipo registro, confirmado com email
        token_data = {'exp': datetime.utcnow() + timedelta(days=1), 'aud': 'registro', 'email': email}
        token = generate_token(request=self.request, data=token_data)
        confirm_url = self.request.route_url('api_confirm', token=token)

        # envio de email de confirmação
        send_async_templated_mail(request=self.request, recipients=email,
                                  template='templates/email/confirm_register',
                                  context=dict(
                                      first_name=fname,
                                      link=confirm_url
                                  ))

        msg = 'Verifique seu email para realizar a confirmação'
        res = dumps(dict(message=msg), ensure_ascii=False)
        return HTTPOk(body=res, content_type='application/json; charset=UTF-8')
