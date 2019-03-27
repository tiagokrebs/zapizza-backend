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
from .models import Cliente
from ..site.hashid import generate_hash
from .schemas import ClienteSchema
from json import dumps
from marshmallow import ValidationError
from marshmallow.utils import is_iterable_but_not_string


@view_defaults(permission='super')
class ClienteViews:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.current_user = request.user

    @view_config(route_name='clientes', renderer='json',
                 request_method='GET')
    def cliente_get_list(self):
        offset = int(self.request.GET.get('start', 0))
        limit = int(self.request.GET.get('size', 10))
        sort = self.request.GET.get('sort', 'nome')
        order = self.request.GET.get('order', 'asc')
        nome = self.request.GET.get('nome')
        ativo = self.request.GET.get('ativo')
        clientes = Cliente.list(self.current_user.empresa_id, offset, limit, sort, order, nome, ativo)
        total = Cliente.total(self.current_user.empresa_id, nome, ativo)[0]
        schema = ClienteSchema(many=is_iterable_but_not_string(clientes), strict=True)
        result = schema.dump(clientes)

        if clientes:
            res = dumps(dict(
                data=dict(
                    code=200,
                    totalItems=total,
                    clientes=result.data)),
                ensure_ascii=False)
            return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

        msg = 'Nenhum registro encontrado'
        res = dumps(dict(error=dict(code=404, message=msg)), ensure_ascii=False)
        return HTTPNotFound(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='clientes', renderer='json',
                 request_method='POST')
    def cliente_add(self):
        json_body = self.request.json_body
        schema = ClienteSchema(many=False, strict=True)

        try:
            cliente = schema.load(json_body)
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
        t = cliente.data
        t.ativo = True
        t.empresa_id = self.current_user.empresa_id
        Session.add(t)
        Session.flush()
        Session.refresh(t)

        # define hash_id dos registros pai e lista de filhos
        t.hash_id = generate_hash('clientes', [self.current_user.empresa_id, t.id])
        for telefone in t.telefones:
            telefone.hash_id = generate_hash('telefones', [self.current_user.empresa_id, telefone.id])
        for endereco in t.enderecos:
            endereco.hash_id = generate_hash('enderecos', [self.current_user.empresa_id, endereco.id])

        # objeto de retorno precisa ser serializado
        result = schema.dump(cliente.data)

        res = dumps(dict(
            data=dict(
                code=200,
                cliente=result.data)),
            ensure_ascii=False)
        return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='clientes_edit', renderer='json',
                 request_method='GET')
    def cliente_get(self):
        cliente = self.context
        schema = ClienteSchema(many=False, strict=True)
        result = schema.dump(cliente)

        if cliente:
            res = dumps(dict(
                data=dict(
                    code=200,
                    cliente=result.data)),
                ensure_ascii=False)
            return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

        msg = 'Nenhum registro encontrado'
        res = dumps(dict(error=dict(code=404, message=msg)), ensure_ascii=False)
        return HTTPNotFound(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='clientes_edit', renderer='json',
                 request_method='PUT')
    def cliente_update(self):
        json_body = self.request.json_body
        schema = ClienteSchema(many=False, strict=True)
        schema.context['user'] = self.request.user

        try:
            cliente = schema.load(json_body)
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

        self.context.nome = cliente.data.nome
        self.context.telefones = cliente.data.telefones
        self.context.enderecos = cliente.data.enderecos

        # com a deserialização ok a inserção é permitida
        Session.flush()
        # Session.refresh()

        # define hash_id dos registros pai e lista de filhos
        self.context.hash_id = generate_hash('clientes', [self.current_user.empresa_id, self.context.id])
        for telefone in self.context.telefones:
            telefone.hash_id = generate_hash('telefones', [self.current_user.empresa_id, telefone.id])
        for endereco in self.context.enderecos:
            endereco.hash_id = generate_hash('enderecos', [self.current_user.empresa_id, endereco.id])

        # objeto de retorno precisa ser serializado
        result = schema.dump(self.context)

        res = dumps(dict(
            data=dict(
                code=200,
                cliente=result.data)),
            ensure_ascii=False)
        return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='clientes_edit', renderer='json',
                 request_method='DELETE')
    def cliente_delete(self):
        t = self.context
        Session.delete(t)

        msg = 'Registro deletado'
        res = dumps(dict(
            data=dict(
                code=200,
                message=msg)),
            ensure_ascii=False)
        return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='clientes_enable', renderer='json',
                 request_method='PUT')
    def cliente_enable(self):
        json_body = self.request.json_body

        if 'ativo' not in json_body:
            msg = 'ativo is required'
            res = dumps(dict(error=dict(code=409, message=msg)), ensure_ascii=False)
            return HTTPBadRequest(body=res, content_type='application/json; charset=UTF-8')
        ativo = json_body['ativo']

        self.context.ativo = ativo

        # objeto de retorno precisa ser serializado
        schema = ClienteSchema(many=False, strict=True)
        result = schema.dump(self.context)

        res = dumps(dict(
            data=dict(
                code=200,
                cliente=result.data)),
            ensure_ascii=False)
        return HTTPOk(body=res, content_type='application/json; charset=UTF-8')
