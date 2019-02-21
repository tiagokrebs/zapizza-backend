from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
from pyramid_sqlalchemy import metadata
from .site.security import groupfinder, get_user, RootFactory
from .site.cors import CorsPreflightPredicate, add_cors_preflight_handler, add_cors_to_response


def main(global_config, **settings):
    config = Configurator(settings=settings, root_factory=RootFactory)

    # adiciona metodos cross origin resource sharing (CORS)
    config.add_directive('add_cors_preflight_handler', add_cors_preflight_handler)
    config.add_route_predicate('cors_preflight', CorsPreflightPredicate)
    config.add_subscriber(add_cors_to_response, 'pyramid.events.NewResponse')
    config.add_cors_preflight_handler()

    # inclui dependencias
    config.include('pyramid_jinja2')
    config.include('pyramid_chameleon')
    config.include('pyramid_sqlalchemy')

    # escaneia views
    config.scan()

    # cria metadados de persistencia
    metadata.create_all()

    # adiciona rodas estaticas
    # config.add_static_view(name='static', path='zapizza.site:static')

    # todo: levar rotas para dentro de seus módulos

    # # API routes
    # config.add_route('api_confirm', '/api/confirm')
    # config.add_route('api_login', '/api/login')
    # config.add_route('api_logout', '/api/logout')
    # config.add_route('api_signup', '/api/signup')
    # config.add_route('api_pass_forgot', '/api/forgot')
    # config.add_route('api_pass_reset', '/api/reset')
    # config.add_route('api_authenticated', '/api/authenticated')
    # config.add_route('api_profile', '/api/user/{username}',
    #                  factory='.users.models.user_factory')

    # rotas site
    config.add_route('confirm', '/confirm')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('signup', '/signup')
    config.add_route('pass_forgot', '/forgot')
    config.add_route('pass_reset', '/reset')
    config.add_route('authenticated', '/authenticated')

    # rotas user
    config.add_route('users_profile', '/user/{username}/profile',
                     factory='.users.models.user_factory')
    # config.add_route('users_list', '/users',
    #                  factory='.users.models.user_factory')
    # config.add_route('users_add', '/users/add',
    #                  factory='.users.models.user_factory')
    # config.add_route('users_delete', '/users/{username}/delete',
    #                  factory='.users.models.user_factory')

    # rotas tamanhos
    config.add_route('tamanhos', '/tamanhos',
                     factory='.pizzas.tamanhos.models.tamanho_factory')
    config.add_route('tamanhos_edit', '/tamanhos/{hashid}',
                     factory='.pizzas.tamanhos.models.tamanho_factory')
    config.add_route('tamanhos_enable', '/tamanhos/{hashid}/enable',
                     factory='.pizzas.tamanhos.models.tamanho_factory')

    # rotas sabores
    config.add_route('sabores', '/sabores',
                     factory='.pizzas.sabores.models.sabor_factory')
    config.add_route('sabores_edit', '/sabores/{hashid}',
                     factory='.pizzas.sabores.models.sabor_factory')
    config.add_route('sabores_enable', '/sabores/{hashid}/enable',
                     factory='.pizzas.sabores.models.sabor_factory')

    # Factory da sessao
    session_secret = settings['session.secret']
    session_factory = SignedCookieSessionFactory(session_secret)
    config.set_session_factory(session_factory)

    # Politicas de segurança
    authn_policy = AuthTktAuthenticationPolicy(
        settings['auth.secret'], callback=groupfinder,
        hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    # Objeto User disponivel como um atributo de Request
    config.add_request_method(get_user, 'user', reify=True)

    # cria aplicacao
    return config.make_wsgi_app()
