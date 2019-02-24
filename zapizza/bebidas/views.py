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
from .models import Bebida
from ..site.hashid import generate_hash
from .schemas import BebidaSchema
from json import dumps
from marshmallow import ValidationError
from marshmallow.utils import is_iterable_but_not_string


@view_defaults(permission='super')
class BebidaViews:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.current_user = request.user

    @view_config(route_name='bebidas', renderer='json',
                 request_method='GET')
    def bebida_get_list(self):
        bebidas = Bebida.list(self.current_user.empresa_id)
        total = Bebida.total(self.current_user.empresa_id)[0]
        schema = BebidaSchema(many=is_iterable_but_not_string(bebidas), strict=True)
        schema.context['user'] = self.request.user
        result = schema.dump(bebidas)

        if bebidas:
            res = dumps(dict(
                data=dict(
                    code=200,
                    totalItems=total,
                    bebidas=result.data)),
                ensure_ascii=False)
            return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

        msg = 'Nenhum registro encontrado'
        res = dumps(dict(error=dict(code=404, message=msg)), ensure_ascii=False)
        return HTTPNotFound(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='bebidas', renderer='json',
                 request_method='POST')
    def bebida_add(self):
        json_body = self.request.json_body
        schema = BebidaSchema(many=False, strict=True)
        schema.context['user'] = self.request.user
        schema.context['bebida'] = self.context

        try:
            bebida = schema.load(json_body)
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
        t = bebida.data
        t.ativo = True
        t.empresa_id = self.current_user.empresa_id
        Session.add(t)
        Session.flush()
        Session.refresh(t)
        t.hash_id = generate_hash('bebidas', [self.current_user.empresa_id, t.id])

        # objeto de retorno precisa ser serializado
        result = schema.dump(bebida.data)

        res = dumps(dict(
            data=dict(
                code=200,
                bebida=result.data)),
            ensure_ascii=False)
        return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='bebidas_edit', renderer='json',
                 request_method='GET')
    def bebida_get(self):
        bebida = self.context
        schema = BebidaSchema(many=False, strict=True)
        schema.context['user'] = self.request.user
        result = schema.dump(bebida)

        if bebida:
            res = dumps(dict(
                data=dict(
                    code=200,
                    bebida=result.data)),
                ensure_ascii=False)
            return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

        msg = 'Nenhum registro encontrado'
        res = dumps(dict(error=dict(code=404, message=msg)), ensure_ascii=False)
        return HTTPNotFound(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='bebidas_edit', renderer='json',
                 request_method='PUT')
    def bebida_update(self):
        json_body = self.request.json_body
        schema = BebidaSchema(many=False, strict=True)
        schema.context['user'] = self.request.user
        schema.context['bebida'] = self.context

        try:
            bebida = schema.load(json_body)
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
        self.context.descricao = bebida.data.descricao
        self.context.valor = bebida.data.valor

        # objeto de retorno precisa ser serializado
        result = schema.dump(self.context)

        res = dumps(dict(
            data=dict(
                code=200,
                bebida=result.data)),
            ensure_ascii=False)
        return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='bebidas_edit', renderer='json',
                 request_method='DELETE')
    def bebida_delete(self):
        t = self.context
        Session.delete(t)

        msg = 'Registro deletado'
        res = dumps(dict(
            data=dict(
                code=200,
                message=msg)),
            ensure_ascii=False)
        return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='bebidas_enable', renderer='json',
                 request_method='PUT')
    def bebida_enable(self):
        json_body = self.request.json_body

        if 'ativo' not in json_body:
            msg = 'ativo is required'
            res = dumps(dict(error=dict(code=409, message=msg)), ensure_ascii=False)
            return HTTPBadRequest(body=res, content_type='application/json; charset=UTF-8')
        ativo = json_body['ativo']

        self.context.ativo = ativo

        # objeto de retorno precisa ser serializado
        schema = BebidaSchema(many=False, strict=True)
        schema.context['user'] = self.request.user
        result = schema.dump(self.context)

        res = dumps(dict(
            data=dict(
                code=200,
                bebida=result.data)),
            ensure_ascii=False)
        return HTTPOk(body=res, content_type='application/json; charset=UTF-8')
