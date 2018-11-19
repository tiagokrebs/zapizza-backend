from pyramid.httpexceptions import (
    HTTPForbidden,
    HTTPInternalServerError,
    HTTPNotFound
)
from pyramid.view import (
    notfound_view_config,
    forbidden_view_config,
    exception_view_config
)
from ..errors import InputError
from json import dumps


class HttpExcepViews:
    def __init__(self, context, request):
        self.request = request
        self.context = context

    # todo: verificar possibilidade de multiplas forbidden view, api e site
    @forbidden_view_config(renderer='json')
    def forbidden(self):
        msg = 'Forbidden'
        url = self.request.url
        res = dumps(dict(type='error', message=msg, url=url), ensure_ascii=False)
        return HTTPForbidden(body=res, content_type='application/json; charset=UTF-8')

    @exception_view_config(InputError)
    def input_error(exc):
        msg = '%s' % exc.context.message
        res = dumps(dict(type='error', message=msg), ensure_ascii=False)
        return HTTPInternalServerError(body=res, content_type='application/json; charset=UTF-8')

    @exception_view_config()
    def internal_error(exc):
        msg = exc.context.args[0]
        res = dumps(dict(type='error', message=msg), ensure_ascii=False)
        return HTTPInternalServerError(body=res, content_type='application/json; charset=UTF-8')

    @notfound_view_config(renderer='json')
    def not_found(self):
        msg = 'Not Found'
        url = self.request.url
        res = dumps(dict(type='error', message=msg, url=url), ensure_ascii=False)
        return HTTPNotFound(body=res, content_type='application/json; charset=UTF-8')
