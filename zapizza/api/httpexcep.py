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
