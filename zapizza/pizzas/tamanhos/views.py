from pyramid.httpexceptions import (
    HTTPFound,
    HTTPOk,
    HTTPNotFound,
    HTTPBadRequest,
    HTTPConflict
)
from pyramid.view import (
    view_config,
    view_defaults
)
from deform import Form, ValidationFailure
from pyramid_sqlalchemy import Session
from .models import Tamanho
from ...site.hashid import generate_hash
from .schemas import TamanhoSchema
from json import dumps
from marshmallow import ValidationError
from marshmallow.utils import is_iterable_but_not_string


@view_defaults(permission='super')
class TamanhoViews:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.current_user = request.user

    @view_config(route_name='tamanhos', renderer='json',
                 request_method='GET')
    def tamanho_get_list(self):
        tamanhos = Tamanho.list(self.current_user.empresa_id)
        schema = TamanhoSchema(many=is_iterable_but_not_string(tamanhos), strict=True)
        result = schema.dump(tamanhos)

        if tamanhos:
            res = dumps(dict(
                data=dict(
                    code=200,
                    tamanhos=result.data)),
                ensure_ascii=False)
            return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

        msg = 'Nenhum registro encontrado'
        res = dumps(dict(error=dict(code=404, message=msg)), ensure_ascii=False)
        return HTTPNotFound(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='tamanhos', renderer='json',
                 request_method='POST')
    def tamanho_add(self):
        json_body = self.request.json_body
        schema = TamanhoSchema(many=False, strict=True)
        schema.context['user'] = self.request.user
        schema.context['tamanho'] = self.context

        try:
            tamanho = schema.load(json_body)
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
        t = tamanho.data
        t.ativo = True
        t.empresa_id = self.current_user.empresa_id
        Session.add(t)
        Session.flush()
        Session.refresh(t)
        t.hash_id = generate_hash('tamanhos', [self.current_user.empresa_id, t.id])

        # objeto de retorno precisa ser serializado
        result = schema.dump(tamanho.data)

        res = dumps(dict(
            data=dict(
                code=200,
                tamanho=result.data)),
            ensure_ascii=False)
        return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='tamanhos_edit', renderer='json',
                 request_method='GET')
    def tamanho_get(self):
        tamanho = self.context
        schema = TamanhoSchema(many=False, strict=True)
        result = schema.dump(tamanho)

        if tamanho:
            res = dumps(dict(
                data=dict(
                    code=200,
                    tamanho=result.data)),
                ensure_ascii=False)
            return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

        msg = 'Nenhum registro encontrado'
        res = dumps(dict(error=dict(code=404, message=msg)), ensure_ascii=False)
        return HTTPNotFound(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='tamanhos_edit', renderer='json',
                 request_method='PUT')
    def tamanho_update(self):
        json_body = self.request.json_body
        schema = TamanhoSchema(many=False, strict=True)
        schema.context['user'] = self.request.user
        schema.context['tamanho'] = self.context

        try:
            tamanho = schema.load(json_body)
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
        self.context.descricao = tamanho.data.descricao
        self.context.sigla = tamanho.data.sigla
        self.context.quant_sabores = tamanho.data.quant_sabores
        self.context.quant_fatias = tamanho.data.quant_fatias
        self.context.quant_bordas = tamanho.data.quant_bordas

        # objeto de retorno precisa ser serializado
        result = schema.dump(self.context)

        res = dumps(dict(
            data=dict(
                code=200,
                tamanho=result.data)),
            ensure_ascii=False)
        return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='tamanhos_edit', renderer='json',
                 request_method='DELETE')
    def tamanho_delete(self):
        t = self.context
        Session.delete(t)

        msg = 'Registro deletado'
        res = dumps(dict(
            data=dict(
                code=200,
                message=msg)),
            ensure_ascii=False)
        return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='tamanhos_enable', renderer='json',
                 request_method='PUT')
    def tamanho_enable(self):
        json_body = self.request.json_body

        if 'ativo' not in json_body:
            msg = 'ativo is required'
            res = dumps(dict(error=dict(code=409, message=msg)), ensure_ascii=False)
            return HTTPBadRequest(body=res, content_type='application/json; charset=UTF-8')
        ativo = json_body['ativo']

        self.context.ativo = ativo

        # objeto de retorno precisa ser serializado
        schema = TamanhoSchema(many=False, strict=True)
        result = schema.dump(self.context)

        res = dumps(dict(
            data=dict(
                code=200,
                tamanho=result.data)),
            ensure_ascii=False)
        return HTTPOk(body=res, content_type='application/json; charset=UTF-8')
