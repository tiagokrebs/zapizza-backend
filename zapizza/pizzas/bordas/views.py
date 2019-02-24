from pyramid.httpexceptions import (
    HTTPOk,
    HTTPNotFound,
    HTTPBadRequest
)
from pyramid.view import (
    view_config,
    view_defaults
)
from pyramid_sqlalchemy import Session
from .models import Borda
from ...site.hashid import generate_hash
from .schemas import BordaSchema
from json import dumps
from marshmallow import ValidationError
from marshmallow.utils import is_iterable_but_not_string


@view_defaults(permission='super')
class BordaViews:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.current_user = request.user

    @view_config(route_name='bordas', renderer='json',
                 request_method='GET')
    def borda_get_list(self):
        bordas = Borda.list(self.current_user.empresa_id)
        total = Borda.total(self.current_user.empresa_id)[0]
        schema = BordaSchema(many=is_iterable_but_not_string(bordas), strict=True)
        schema.context['user'] = self.request.user
        result = schema.dump(bordas)

        if bordas:
            res = dumps(dict(
                data=dict(
                    code=200,
                    totalItems=total,
                    bordas=result.data)),
                ensure_ascii=False)
            return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

        msg = 'Nenhum registro encontrado'
        res = dumps(dict(error=dict(code=404, message=msg)), ensure_ascii=False)
        return HTTPNotFound(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='bordas', renderer='json',
                 request_method='POST')
    def borda_add(self):
        json_body = self.request.json_body
        schema = BordaSchema(many=False, strict=True)
        schema.context['user'] = self.request.user
        schema.context['borda'] = self.context

        try:
            borda = schema.load(json_body)
        except ValidationError as err:
            errors = err.messages

            error_list = []
            for k, v in errors.items():
                error_list.append({'field': k, 'message': v})

            msg = 'Dados inválidos'
            res = dumps(dict(
                error=dict(
                    code=400,
                    message=msg,
                    errors=error_list)),
                ensure_ascii=False)
            return HTTPBadRequest(body=res, content_type='application/json; charset=UTF-8')

        # com a deserialização ok a inserção é permitida
        t = borda.data
        t.ativo = True
        t.empresa_id = self.current_user.empresa_id
        Session.add(t)
        Session.flush()
        Session.refresh(t)
        t.hash_id = generate_hash('bordas', [self.current_user.empresa_id, t.id])

        # objeto de retorno precisa ser serializado
        result = schema.dump(borda.data)

        res = dumps(dict(
            data=dict(
                code=200,
                borda=result.data)),
            ensure_ascii=False)
        return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='bordas_edit', renderer='json',
                 request_method='GET')
    def borda_get(self):
        borda = self.context
        schema = BordaSchema(many=False, strict=True)
        schema.context['user'] = self.request.user
        result = schema.dump(borda)

        if borda:
            res = dumps(dict(
                data=dict(
                    code=200,
                    borda=result.data)),
                ensure_ascii=False)
            return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

        msg = 'Nenhum registro encontrado'
        res = dumps(dict(error=dict(code=404, message=msg)), ensure_ascii=False)
        return HTTPNotFound(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='bordas_edit', renderer='json',
                 request_method='PUT')
    def borda_update(self):
        json_body = self.request.json_body
        schema = BordaSchema(many=False, strict=True)
        schema.context['user'] = self.request.user
        schema.context['borda'] = self.context

        try:
            borda = schema.load(json_body)
        except ValidationError as err:
            errors = err.messages

            error_list = []
            for k, v in errors.items():
                error_list.append({'field': k, 'message': v})

            msg = 'Dados inválidos'
            res = dumps(dict(
                error=dict(
                    code=400,
                    message=msg,
                    errors=error_list)),
                ensure_ascii=False)
            return HTTPBadRequest(body=res, content_type='application/json; charset=UTF-8')

        # com a deserialização ok a atualização é permitida
        self.context.descricao = borda.data.descricao
        self.context.valor = borda.data.valor

        # objeto de retorno precisa ser serializado
        result = schema.dump(self.context)

        res = dumps(dict(
            data=dict(
                code=200,
                borda=result.data)),
            ensure_ascii=False)
        return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='bordas_edit', renderer='json',
                 request_method='DELETE')
    def borda_delete(self):
        t = self.context
        Session.delete(t)

        msg = 'Registro deletado'
        res = dumps(dict(
            data=dict(
                code=200,
                message=msg)),
            ensure_ascii=False)
        return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='bordas_enable', renderer='json',
                 request_method='PUT')
    def borda_enable(self):
        json_body = self.request.json_body

        if 'ativo' not in json_body:
            msg = 'ativo is required'
            res = dumps(dict(error=dict(code=409, message=msg)), ensure_ascii=False)
            return HTTPBadRequest(body=res, content_type='application/json; charset=UTF-8')
        ativo = json_body['ativo']

        self.context.ativo = ativo

        # objeto de retorno precisa ser serializado
        schema = BordaSchema(many=False, strict=True)
        schema.context['user'] = self.request.user
        result = schema.dump(self.context)

        res = dumps(dict(
            data=dict(
                code=200,
                borda=result.data)),
            ensure_ascii=False)
        return HTTPOk(body=res, content_type='application/json; charset=UTF-8')
