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
from .models import Pedido
from ..site.hashid import generate_hash
from .schemas import PedidoSchema
from json import dumps
from marshmallow import ValidationError
from marshmallow.utils import is_iterable_but_not_string
from sqlalchemy.sql.functions import now


@view_defaults(permission='super')
class PedidoViews:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.current_user = request.user

    @view_config(route_name='pedidos', renderer='json',
                 request_method='GET')
    def pedido_get_list(self):
        offset = int(self.request.GET.get('start', 0))
        limit = int(self.request.GET.get('size', 10))
        sort = self.request.GET.get('sort', 'finalizacao')
        order = self.request.GET.get('order', 'asc')
        cliente = self.request.GET.get('cliente')

        pedidos = Pedido.list(self.current_user.empresa_id, offset, limit, sort, order, cliente)
        total = Pedido.total(self.current_user.empresa_id, cliente)[0]
        schema = PedidoSchema(many=is_iterable_but_not_string(pedidos), strict=True)
        schema.context['user'] = self.request.user

        result = schema.dump(pedidos)

        if pedidos:
            res = dumps(dict(
                data=dict(
                    code=200,
                    totalItems=total,
                    pedidos=result.data)),
                ensure_ascii=False)
            return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

        msg = 'Nenhum registro encontrado'
        res = dumps(dict(error=dict(code=404, message=msg)), ensure_ascii=False)
        return HTTPNotFound(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='pedidos', renderer='json',
                 request_method='POST')
    def pedido_add(self):
        json_body = self.request.json_body
        schema = PedidoSchema(many=False, strict=True)
        schema.context['user'] = self.request.user
        schema.context['pedido'] = self.context

        try:
            pedido = schema.load(json_body)
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
        t = pedido.data
        t.empresa_id = self.current_user.empresa_id
        Session.add(t)
        Session.flush()
        Session.refresh(t)
        t.hash_id = generate_hash('pedidos', [self.current_user.empresa_id, t.id])

        # objeto de retorno precisa ser serializado
        result = schema.dump(pedido.data)

        res = dumps(dict(
            data=dict(
                code=200,
                pedido=result.data)),
            ensure_ascii=False)
        return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='pedidos_edit', renderer='json',
                 request_method='GET')
    def pedido_get(self):
        pedido = self.context
        schema = PedidoSchema(many=False, strict=True)
        schema.context['user'] = self.request.user
        result = schema.dump(pedido)

        if pedido:
            res = dumps(dict(
                data=dict(
                    code=200,
                    pedido=result.data)),
                ensure_ascii=False)
            return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

        msg = 'Nenhum registro encontrado'
        res = dumps(dict(error=dict(code=404, message=msg)), ensure_ascii=False)
        return HTTPNotFound(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='pedidos_edit', renderer='json',
                 request_method='PUT')
    def pedido_update(self):
        json_body = self.request.json_body
        schema = PedidoSchema(many=False, strict=True)
        schema.context['user'] = self.request.user
        schema.context['pedido'] = self.context

        try:
            pedido = schema.load(json_body)
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
        self.context.finalizacao = now()
        self.context.cliente_id = pedido.data.cliente_id
        self.context.pedido_json = pedido.data.pedido_json
        self.context.tipo_entrega = pedido.data.tipo_entrega
        self.context.endereco_id = pedido.data.endereco_id
        self.context.obs_entrega = pedido.data.obs_entrega
        self.context.valor_total = pedido.data.valor_total

        # objeto de retorno precisa ser serializado
        result = schema.dump(self.context)

        res = dumps(dict(
            data=dict(
                code=200,
                pedido=result.data)),
            ensure_ascii=False)
        return HTTPOk(body=res, content_type='application/json; charset=UTF-8')
