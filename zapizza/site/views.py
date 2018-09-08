from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget
from pyramid.view import (
    view_config,
    notfound_view_config,
    forbidden_view_config
)
import re
from ..users.models import User
from ..site.token import confirm_token
from ..site.email import send_async_templated_mail
from ..site.token import generate_token
from datetime import datetime, timedelta
from pyramid_sqlalchemy import Session


class SiteViews:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.primary_messages = request.session.pop_flash('primary')
        self.success_messages = request.session.pop_flash('success')
        self.danger_messages = request.session.pop_flash('danger')
        self.warning_messages = request.session.pop_flash('warning')
        self.current_user = User.by_username(request.authenticated_userid)

    @view_config(route_name='home', renderer='templates/home.jinja2')
    def home(self):
        return dict(primary_messages=self.primary_messages,
                    success_messages=self.success_messages,
                    danger_messages=self.danger_messages,
                    warning_messages=self.warning_messages)

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
                return HTTPFound(location=request.route_url('register', _query=dict(new=email)))

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
        Após o login caso efetuado com sucesso a url de came_from é utilizada ao invés de /home
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
        user = User.by_username_email(username)
        if user and user.password == password:
            headers = remember(request, user.username)
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
        # todo: utilizar Deform + colander para formulário de registro
        try:
            email = self.request.params['new']
        except:
            return dict()
        return dict(email=email)

    # todo: utilizar Dform + Schema para validação dos atributos ver user_edit_profile
    @view_config(route_name='register', renderer='templates/register.jinja2',
                 request_method='POST')
    def register_handler(self):
        # todo: utilizar Deform + colander para validação do registro
        request = self.request
        email = request.params['email']
        username = request.params['username']
        password = request.params['password']
        cpassword = request.params['cpassword']
        fname = request.params['fname']
        lname = request.params['lname']

        # verifica existência de email
        if not email:
            return dict(
                form_error='Informe um e-mail', email=email,
                username=username, fname=fname, lname=lname
                )

        # verifica uso de email por usuário existente
        if User.by_username(email):
            return dict(
                form_error='O e-mail informado já está cadastrado',
                email=email,
                username=username, fname=fname, lname=lname
            )

        # verifica regex mínimo para email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return dict(
                form_error='Informe um e-mail válido',
                email=email,
                username=username, fname=fname, lname=lname
            )

        # verifica existência de username
        if not username:
            return dict(
                form_error='Informe um usernamme',
                email=email,
                username=username, fname=fname, lname=lname
            )

        # verifica uso de username por usuário existente
        if User.by_username(username):
            return dict(
                form_error='O username informado já está cadastrado',
                email=email,
                username=username, fname=fname, lname=lname
            )

        # verifica regex mínimo para username
        if not re.match(r"^[a-zA-Z0-9]{3,120}$", username):
            return dict(
                form_error='Username inválido',
                email=email,
                username=username, fname=fname, lname=lname
            )

        # verifica existência de password
        if not password:
            return dict(
                form_error='Informe um password',
                email=email,
                username=username, fname=fname, lname=lname
            )

        # verifica regex mínimo para password
        if not re.match(r".{6,120}", password):
            return dict(
                form_error='Informe um passord contendo no mínimo 6 caracteres',
                email=email,
                username=username, fname=fname, lname=lname
            )

        # verifica existência de cpassword
        if not cpassword:
            return dict(
                form_error='Informe a confirmação do password',
                email=email,
                username=username, fname=fname, lname=lname
            )

        # verifia igualdadade entre passwords
        if cpassword != password:
            return dict(
                form_error='A confirmação do password incorreta',
                email=email,
                username=username, fname=fname, lname=lname
            )

        # verifica existência de fname
        if not fname:
            return dict(
                form_error='Informe o primeiro nome',
                email=email,
                username=username, fname=fname, lname=lname
            )

        # verifica regex mínimo para fname
        if fname and not re.match(r"^[a-zA-Z]{3,120}$", fname):
            return dict(
                form_error='Primeiro nome inválido',
                email=email,
                username=username, fname=fname, lname=lname
            )

        # verifica existência de lname
        if not lname:
            return dict(
                form_error='Informe o último nome',
                email=email,
                username=username, fname=fname, lname=lname
            )

        # verifica regex mínimo para lname
        if lname and not re.match(r"^[a-zA-Z]{3,120}$", lname):
            return dict(
                form_error='Último nome inválido',
                email=email,
                username=username, fname=fname, lname=lname
            )

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
                                  template='templates/email/confirm_register',
                                  context=dict(
                                      first_name=fname,
                                      link=confirm_url
                                  ))

        if user:
            form_error = 'Verifique seu email para realizar a confirmação'
            return dict(form_error=form_error, user=user)

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
                # retorna página de confirmação com termos de aceite
                return dict()

        return dict(form_alert='Token inválido', invalid_token='true')

    @view_config(route_name='confirm',
                 permission='super',
                 renderer='templates/confirm.jinja2',
                 request_method='POST')
    def confirm_handler(self):
        """
        Confirmação dos termos de aceite registra o usuário e gera aviso 
        """
        if 'confirm.submitted' in self.request.params:
            check = self.request.params.getall("aceito")
            if check and check[0] == 'aceito':
                # registra usuário e direciona para home
                self.current_user.register_confirm = datetime.utcnow()
                url = self.request.route_url('home')
                return HTTPFound(url)

            return dict(form_alert='Você precisa aceitar os termos e condições')

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
            else:
                return dict(form_alert='Email não registrado')

    @view_config(route_name='forgot',
                 renderer='templates/forgot.jinja2')
    def forgot(self):
        return dict()

    @view_config(route_name='forgot', renderer='templates/forgot.jinja2',
                 request_method='POST')
    def forgot_handler(self):
        request = self.request
        email = request.params['email']
        if not email:
            return dict(
                form_error='Informe um e-mail',
                email=email
            )
        else:
            # verifica se o email informado existe
            if not User.by_username(email):
                return dict(
                    form_error='E-mail informado não encontrado',
                    email=email,
                )
            # envia email de confirmação de senha com token
            else:
                user = User.by_username(email)

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
                    form_error = 'Verifique seu email para realizar a recuperação da senha'
                    return dict(form_error=form_error, user=user)

    @view_config(route_name='reset',
                 renderer='templates/reset.jinja2')
    def reset(self):
        """
        Validação de token de cofirmação de recuperação de senha do usuário
        Caso o token seja válido o usuário é confirmado e redirecionado para a página de recuperação
        Caso o token esteja vencido um alerta é exibido
        """
        token = self.request.matchdict.get('token')
        token_data = confirm_token(request=self.request, token=token, audience='senha')
        if token_data:
            aud = token_data['aud']
            email = token_data['email']
            user = User.by_username(email)
            if user and aud == 'senha':
                # direciona para página de recuperação de senha
                return dict()

        return dict(form_block='Token inválido')

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
                user = User.by_username(email)
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
                    #Session.query(user).filter(user.email == email). \
                    #    update({user.password: password}, synchorize_session=False)
                    user.password = password
                    url = self.request.route_url('login')
                    return HTTPFound(url)

        return dict(form_error='Token inválido')
