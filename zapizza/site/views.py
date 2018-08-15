from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import remember, forget
from pyramid.view import (
    view_config,
    notfound_view_config,
    forbidden_view_config
)
import re
from ..users.models import User
from ..site.token import confirm_token
from zapizza.email import send_async_templated_mail
from ..site.token import generate_token
from datetime import datetime, timedelta
from pyramid_sqlalchemy import Session


class SiteViews:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.current_user = User.by_username(request.authenticated_userid)

    @view_config(route_name='home', renderer='templates/home.jinja2')
    def home(self):
        return dict()

    @view_config(route_name='home', renderer='templates/home.jinja2',
                 request_method='POST')
    def home_register_handler(self):
        request = self.request
        email = request.params['email']
        if email:
            # verifica se o email informado já existe
            if User.by_username(email):
                return dict(
                    form_error='O e-mail informado já está cadastrado',
                    email=email,
                )
            # verifica validade minima do email
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return dict(
                    form_error='Informe um e-mail válido',
                    email=email,
                )
            # redireciona para página de registro
            else:
                # return HTTPFound(location=request.route_url('users_register', _query=dict(email=email)))
                return HTTPFound(location=request.route_url('register', _query=dict(email=email)))

        # retorna apenas mensagem
        return dict(
            form_error='Informe um e-mail',
            email=email
            )

    @notfound_view_config(renderer='templates/notfound.jinja2')
    def not_found(self):
        return dict()

    @forbidden_view_config()
    def forbidden(self):
        """
        Ao encontrar uma rota não autorizada usuário é direcionado para /login
        Origem da requisição é armazenada em came_from como input hiden em template de login
        Após o login caso efetuado com sucesso a url de came_from é utilizada ao invé de /home
        """
        request = self.request
        login_url = request.route_url('login')
        referrer = request.url
        if referrer == login_url:
            referrer = '/'  # não usar referrer igual url de login
        came_from = request.params.get('came_from', referrer)
        url = self.request.route_url('login', _query=dict(came_from=came_from))
        return HTTPFound(url)

    @view_config(route_name='login', renderer='templates/login.jinja2')
    def login(self):
        try:
            came_from = self.request.params['came_from']
        except:
            return dict()
        return dict(came_from=came_from)

    @view_config(route_name='login', renderer='templates/login.jinja2',
                 request_method='POST')
    def login_handler(self):
        request = self.request
        username = request.params['username']
        password = request.params['password']
        came_from = request.params['came_from']
        user = User.by_username(username)
        if user and user.password == password:
            headers = remember(request, username)
            if came_from:
                return HTTPFound(location=came_from,
                                 headers=headers)
            else:
                return HTTPFound(location=request.route_url('home'),
                                 headers=headers)

        return dict(
            form_error='Username ou senha inválidos',
            username=username,
            password=password,
        )

    @view_config(route_name='logout')
    def logout(self):
        headers = forget(self.request)
        url = self.request.route_url('home')
        return HTTPFound(location=url, headers=headers)

    @view_config(route_name='register', renderer='templates/register.jinja2')
    def register(self):
        email = self.request.params['email']
        return dict(email=email)

    @view_config(route_name='register', renderer='templates/register.jinja2',
                 request_method='POST')
    def register_handler(self):
        request = self.request
        email = request.params['email']
        username = request.params['username']
        password = request.params['password']
        cpassword = request.params['cpassword']
        fname = request.params['fname']
        lname = request.params['lname']

        # validações de obrigatoriedade
        # validação de senha confirmada

        groups = ['group:admins', 'group:editors']
        Session.add(User(
            email=email, username=username,
            password=password, first_name=fname,
            last_name=lname, groups=groups
        ))
        user = User.by_username(username)

        # token expira em 24h, tipo registro, confirmado com email
        token_data = {'exp': datetime.utcnow() + timedelta(days=1), 'aud': 'registro', 'email': email}
        token = generate_token(request=self.request, data=token_data)
        confirm_url = self.request.route_url('confirm', token=token)

        # envio de email de confirmação
        send_async_templated_mail(request=self.request, recipients=email,
                                  template='users/templates/email/confirm_register',
                                  context=dict(
                                      first_name=fname,
                                      link=confirm_url
                                  ))

        if user:
            msg = 'Verifique seu email para realizar a confirmação'
            return dict(msg=msg, user=user)

    @view_config(route_name='confirm',
                 permission='super',
                 renderer='templates/confirm.jinja2')
    def confirm(self):
        """
        Validação de token de cofirmação de registro do usuário
        Caso o token seja válido o usuário é confirmado e redirecionado para a home
        Caso o usuário já tenha sido confirmado é direcionado para a home
        Caso o token esteja vencido a solicitação do reenvio do token de confirmação é disponibilizada
        """
        token = self.request.matchdict.get('token')
        token_data = confirm_token(request=self.request, token=token, audience='registro')
        if token_data:
            aud = token_data['aud']
            email = token_data['email']
            user = User.by_username(email)
            if self.current_user and aud == 'registro' and self.current_user.email == user.email:
                # usuário já registrado direcionado para home
                if self.current_user.register_confirm:
                    url = self.request.route_url('home')
                    return HTTPFound(url)

                # registra usuário e direciona para home
                self.current_user.register_confirm = datetime.utcnow()
                return dict(form_alert='Registro efetuado com sucesso')

        """ 
        Solicitação de reenvio de token para email registrado anteriormente
        Utilizado em casos em que o token está vencido
        Caso o email não tenha um registro uma mensagem de aviso é retornada
        Caso o email tenha registro e coincida com o usuário logado um novo email de
        confirmação é enviado
        """
        if 'resend.submitted' in self.request.params:
            email = self.request.params['email']
            user = User.by_username(email)

            if self.current_user and user and self.current_user.email == user.email:
                # token expira em 24h, tipo registro, confirmado com email
                token_data = {'exp': datetime.utcnow() + timedelta(days=1), 'aud': 'registro', 'email': email}
                token = generate_token(request=self.request, data=token_data)
                confirm_url = self.request.route_url('confirm', token=token)
                # envio de email de confirmação
                send_async_templated_mail(request=self.request, recipients=email,
                                          template='users/templates/email/confirm_register',
                                          context=dict(
                                              first_name=self.current_user.first_name,
                                              link=confirm_url
                                          ))
                return dict(form_alert='Email de confirmação enviado')
            else:
                return dict(form_alert='Email não registrado')

        return dict(form_alert='Token inválido')
