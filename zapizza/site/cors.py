from pyramid.security import NO_PERMISSION_REQUIRED

# def includeme(config):
#     config.add_directive(
#         'add_cors_preflight_handler', add_cors_preflight_handler)
#     config.add_route_predicate('cors_preflight', CorsPreflightPredicate)
#
#     config.add_subscriber(add_cors_to_response, 'pyramid.events.NewResponse')


class CorsPreflightPredicate(object):
    def __init__(self, val, config):
        self.val = val

    def text(self):
        return 'cors_preflight = %s' % bool(self.val)

    phash = text

    def __call__(self, context, request):
        if not self.val:
            return False
        return (
            request.method == 'OPTIONS' and
            'Origin' in request.headers and
            'Access-Control-Request-Method' in request.headers
        )


def add_cors_preflight_handler(config):
    config.add_route(
        'cors-options-preflight', '/{catch_all:.*}',
        cors_preflight=True,
    )
    config.add_view(
        cors_options_view,
        route_name='cors-options-preflight',
        permission=NO_PERMISSION_REQUIRED,
    )


def add_cors_to_response(event):
    request = event.request
    response = event.response
    if 'Origin' in request.headers:
        response.headers['Access-Control-Expose-Headers'] = (
            'Content-Type,Date,Content-Length,Authorization,X-Request-ID')

        # ambientes de desenvolvimento podem necessitar de permissão para diversas origens
        response.headers['Access-Control-Allow-Origin'] = (
            request.headers['Origin'])

        # ambientes de produção devem ter origens controladas
        # response.headers['Access-Control-Allow-Origin'] = (
        #     request.registry.settings["cors.origin"])

        response.headers['Access-Control-Allow-Credentials'] = 'true'


def cors_options_view(context, request):
    """Na aplicação frontend axios não envia Access-Control-Request-Headers
        ao fazer requisições do tipo DELETE mas apenas Access-Control-Request-Method.
        Os dois parâmetros são procurados nos headers e caso um esteja disponivel
        então Access-Control-Allow-Methods é retornado"""

    response = request.response
    if 'Access-Control-Request-Headers' in request.headers \
            or 'Access-Control-Request-Method' in request.headers:
        response.headers['Access-Control-Allow-Methods'] = (
            'OPTIONS,HEAD,GET,POST,PUT,DELETE')
    response.headers['Access-Control-Allow-Headers'] = (
        'Content-Type,Accept,Accept-Language,Authorization,X-Request-ID')
    return response
