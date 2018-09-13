from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
from pyramid_sqlalchemy import metadata
from .site.security import groupfinder


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.include('pyramid_chameleon')
    config.scan()
    config.include('pyramid_sqlalchemy')
    metadata.create_all()
    config.add_static_view(name='static', path='zapizza.site:static')

    # Site routes
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('register', '/register')
    config.add_route('confirm', '/confirm/{token}', factory='.users.models.user_factory')
    config.add_route('forgot', '/forgot')
    config.add_route('reset', '/reset/{token}', factory='.users.models.user_factory')

    # Rotas Users com route factory
    config.add_route('users_list', '/users',
                     factory='.users.models.user_factory')
    config.add_route('users_add', '/users/add',
                     factory='.users.models.user_factory')
    config.add_route('users_view', '/users/{username}',
                     factory='.users.models.user_factory')
    config.add_route('users_profile_edit', '/users/{username}/profile',
                     factory='.users.models.user_factory')
    config.add_route('users_delete', '/users/{username}/delete',
                     factory='.users.models.user_factory')

    # Rotas Tamanhos com route factory
    config.add_route('tamanhos_list', '/tamanhos',
                     factory='.tamanhos.models.tamanho_factory')
    config.add_route('tamanhos_add', '/tamanhos/add',
                     factory='.tamanhos.models.tamanho_factory')
    config.add_route('tamanhos_edit', '/tamanhos/{hashid}/edit',
                     factory='.tamanhos.models.tamanho_factory')
    config.add_route('tamanhos_enable', '/tamanhos/{hashid}/enable',
                     factory='.tamanhos.models.tamanho_factory')
    config.add_route('tamanhos_disable', '/tamanhos/{hashid}/disable',
                     factory='.tamanhos.models.tamanho_factory')

    # To Do routes with route factory
    config.add_route('todos_list', '/todos',
                     factory='.todos.models.todo_factory')
    config.add_route('todos_add', '/todos/add',
                     factory='.todos.models.todo_factory')
    config.add_route('todos_view', '/todos/{id}',
                     factory='.todos.models.todo_factory')
    config.add_route('todos_edit', '/todos/{id}/edit',
                     factory='.todos.models.todo_factory')
    config.add_route('todos_delete', '/todos/{id}/delete',
                     factory='.todos.models.todo_factory')

    # Factory da sessão
    session_secret = settings['session.secret']
    session_factory = SignedCookieSessionFactory(session_secret)
    config.set_session_factory(session_factory)

    # Políticas de segurança
    authn_policy = AuthTktAuthenticationPolicy(
        settings['auth.secret'], callback=groupfinder,
        hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    return config.make_wsgi_app()
