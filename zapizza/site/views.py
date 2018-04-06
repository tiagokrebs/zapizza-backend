from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget
from pyramid.view import (
    view_config,
    notfound_view_config,
    forbidden_view_config
)

from pyramid_sqlalchemy import Session

from ..users.models import User


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
    def register_handler(self):
        request = self.request
        email = request.params['email']
        if email:
            headers = remember(request, email)
            return HTTPFound(location=request.route_url('home'),
                             headers=headers)

        return dict(
            form_error='Invalid email',
            email=email,
        )

    @notfound_view_config(renderer='templates/notfound.jinja2')
    def not_found(self):
        return dict()

    @forbidden_view_config(renderer='templates/forbidden.jinja2')
    def forbidden(self):
        return dict()

    @view_config(route_name='login', renderer='templates/login.jinja2')
    def login(self):
        return dict()

    @view_config(route_name='login', renderer='templates/login.jinja2',
                 request_method='POST')
    def login_handler(self):
        request = self.request
        username = request.params['username']
        password = request.params['password']
        user = User.by_username(username)
        if user and user.password == password:
            headers = remember(request, username)
            return HTTPFound(location=request.route_url('home'),
                             headers=headers)

        return dict(
            form_error='Invalid username or password',
            username=username,
            password=password,
        )

    @view_config(route_name='logout')
    def logout(self):
        headers = forget(self.request)
        url = self.request.route_url('home')
        return HTTPFound(location=url, headers=headers)
