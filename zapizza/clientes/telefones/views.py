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
from .models import Telefone
from ...site.hashid import generate_hash, get_decoded_id
from .schemas import TelefoneSchema
from json import dumps
from marshmallow import ValidationError
from marshmallow.utils import is_iterable_but_not_string


@view_defaults(permission='super')
class TelefoneViews:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.current_user = request.user

    @view_config(route_name='telefones', renderer='json',
                 request_method='GET')
    def telefone_get_list(self):
        cliente_hash_id = self.request.matchdict.get('cliHashid')
        cliente_id = get_decoded_id('clientes', cliente_hash_id, self.current_user.empresa_id)

        telefones = Telefone.list(cliente_id)
        schema = TelefoneSchema(many=is_iterable_but_not_string(telefones), strict=True)
        result = schema.dump(telefones)

        if telefones:
            res = dumps(dict(
                data=dict(
                    code=200,
                    telefones=result.data)),
                ensure_ascii=False)
            return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

        msg = 'Nenhum registro encontrado'
        res = dumps(dict(error=dict(code=404, message=msg)), ensure_ascii=False)
        return HTTPNotFound(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='telefones', renderer='json',
                 request_method='POST')
    def telefone_add(self):
        json_body = self.request.json_body

        """
        A fim de evitar o carregamento de objeto Cliente + filhos
        e o uso de relationship com lazy load nos modelos
        cliente_id é obtido de cliHashid e adicionado ao objeto
        Telefone deserializado através de TelefoneSchema mais tarde
        """
        cliente_hash_id = self.request.matchdict.get('cliHashid')
        cliente_id = get_decoded_id('clientes', cliente_hash_id, self.current_user.empresa_id)

        schema = TelefoneSchema(many=False, strict=True)
        schema.context['cliente_id'] = cliente_id
        schema.context['telefone'] = self.context.telefone
        try:
            telefone = schema.load(json_body)
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
        t = telefone.data
        t.cliente_id = cliente_id
        Session.add(t)
        Session.flush()
        Session.refresh(t)
        t.hash_id = generate_hash('telefones', [self.current_user.empresa_id, t.id])

        # objeto de retorno precisa ser serializado
        result = schema.dump(telefone.data)

        res = dumps(dict(
            data=dict(
                code=200,
                telefone=result.data)),
            ensure_ascii=False)
        return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='telefones_edit', renderer='json',
                 request_method='GET')
    def telefone_get(self):
        telefone = self.context
        schema = TelefoneSchema(many=False, strict=True)
        result = schema.dump(telefone)

        if telefone:
            res = dumps(dict(
                data=dict(
                    code=200,
                    telefone=result.data)),
                ensure_ascii=False)
            return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

        msg = 'Nenhum registro encontrado'
        res = dumps(dict(error=dict(code=404, message=msg)), ensure_ascii=False)
        return HTTPNotFound(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='telefones_edit', renderer='json',
                 request_method='PUT')
    def telefone_update(self):
        json_body = self.request.json_body
        cliente_hash_id = self.request.matchdict.get('cliHashid')
        cliente_id = get_decoded_id('clientes', cliente_hash_id, self.current_user.empresa_id)

        schema = TelefoneSchema(many=False, strict=True)
        schema.context['cliente_id'] = cliente_id
        schema.context['telefone'] = self.context.telefone

        try:
            telefone = schema.load(json_body)
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
        self.context.telefone = telefone.data.telefone

        # objeto de retorno precisa ser serializado
        result = schema.dump(self.context)

        res = dumps(dict(
            data=dict(
                code=200,
                telefone=result.data)),
            ensure_ascii=False)
        return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='telefones_edit', renderer='json',
                 request_method='DELETE')
    def telefone_delete(self):
        t = self.context
        Session.delete(t)

        msg = 'Registro deletado'
        res = dumps(dict(
            data=dict(
                code=200,
                message=msg)),
            ensure_ascii=False)
        return HTTPOk(body=res, content_type='application/json; charset=UTF-8')
