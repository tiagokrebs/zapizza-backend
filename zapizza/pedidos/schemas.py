from marshmallow import (
    Schema,
    fields,
    post_load,
    post_dump,
    ValidationError,
    validates,
    validate
)
from .models import Pedido
from pyramid.httpexceptions import HTTPForbidden
from ..adicionais.models import Adicional
from ..pizzas.sabores.models import Sabor
from ..pizzas.bordas.models import Borda
from ..pizzas.tamanhos.models import Tamanho
from ..clientes.enderecos.models import Endereco
from ..clientes.models import Cliente
from ..site.hashid import generate_hash


class PedidoAdicionalSchema(Schema):
    hash_id = fields.String(required=True)
    valor = fields.Number(required=True)

    @validates('hash_id')
    def validate_hash_id(self, value):
        """
        Valida existência do adicional
        :param value: valor do atributo hash_id
        :return: nulo ou ValidationError
        """
        try:
            Adicional.by_hash_id(self.context['user'].empresa_id, value)
        except HTTPForbidden as err:
            raise ValidationError('Adicional não encontrado')

    # todo: validar valor do adicional


class PedidoSaboresSchema(Schema):
    hash_id = fields.String(required=True)
    valor = fields.Number(required=True)

    @validates('hash_id')
    def validate_hash_id(self, value):
        """
        Valida existência do sabor
        :param value: valor do atributo hash_id
        :return: nulo ou ValidationError
        """
        try:
            Sabor.by_hash_id(self.context['user'].empresa_id, value)
        except HTTPForbidden as err:
            raise ValidationError('Sabor não encontrado')

    # todo: validar valor do sabor de acordo com o tamanho


class PedidoBordasSchema(Schema):
    hash_id = fields.String(required=True)
    valor = fields.Number(required=True)

    @validates('hash_id')
    def validate_hash_id(self, value):
        """
        Valida existência da borda
        :param value: valor do atributo hash_id
        :return: nulo ou ValidationError
        """
        try:
            Borda.by_hash_id(self.context['user'].empresa_id, value)
        except HTTPForbidden as err:
            raise ValidationError('Borda não encontrada')

    # todo: validar valor da borda


class PedidoPizzaSchema(Schema):
    tamanho = fields.String(required=True)
    sabores = fields.Nested(PedidoSaboresSchema, required=True, many=True, validate=validate.Length(min=1))
    bordas = fields.Nested(PedidoBordasSchema, required=True, many=True)

    @validates('tamanho')
    def validate_hash_id(self, value):
        """
        Valida existência do tamanho
        :param value: valor do atributo tamanho
        :return: nulo ou ValidationError
        """
        try:
            Tamanho.by_hash_id(self.context['user'].empresa_id, value)
        except HTTPForbidden as err:
            raise ValidationError('Tamanho não encontrado')

    # todo: validar quantidade de sabores e bordas de acordo com o tamanho


class PedidoProdutosSchema(Schema):
    adicionais = fields.Nested(PedidoAdicionalSchema, required=True, many=True)
    pizzas = fields.Nested(PedidoPizzaSchema, required=True, many=True,
                          validate=validate.Length(min=1))


class PedidoClienteSchema(Schema):
    nome = fields.String()


class PedidoSchema(Schema):
    hash_id = fields.String()
    finalizacao = fields.DateTime()
    cliente_id = fields.String(required=True, validate=validate.Length(min=6, max=120))
    pedido_json = fields.Nested(PedidoProdutosSchema, required=True, many=False)
    tipo_entrega = fields.String(required=True, validate=validate.OneOf(['B', 'E']))
    endereco_id = fields.String(required=True, validate=validate.Length(min=6, max=120))
    obs_entrega = fields.String()
    valor_total = fields.Number(required=True, validate=validate.Range(min=0))
    cliente = fields.Nested(PedidoClienteSchema, many=False)

    @post_load
    def make_pedido(self, data):
        """
        No pós serialização cliente_id e endereco_id mudam de hash_id para id
        :param data: dados do objeto a ser deserializado
        :return: instância de Pedido
        """
        e = Endereco.by_hash_id(self.context['user'].empresa_id, data['endereco_id'])
        data['endereco_id'] = e.id

        c = Cliente.by_hash_id(self.context['user'].empresa_id, data['cliente_id'])
        data['cliente_id'] = c.id

        return Pedido(**data)

    @post_dump(pass_many=True)
    def encode_id(self, data, many):
        """
        No pós serialização cliente_id e endereco_id são codificado para hash_id

        :param data: dados do objeto a ser serializadp
        :param many: true/false indica se objeto é uma lista
        :return: dados com id codificado
        """
        for d in data:
            encoded_endereco_id = generate_hash('enderecos', [self.context['user'].empresa_id, int(d['endereco_id'])])
            d['endereco_id'] = encoded_endereco_id

            encoded_cliente_id = generate_hash('clientes', [self.context['user'].empresa_id, int(d['cliente_id'])])
            d['cliente_id'] = encoded_cliente_id

        return data

    @validates('cliente_id')
    def validate_cliente_id(self, value):
        """
        Valida existência do cliente
        :param value: valor do atributo cliente_id
        :return: nulo ou ValidationError
        """
        try:
            Cliente.by_hash_id(self.context['user'].empresa_id, value)
        except HTTPForbidden as err:
            raise ValidationError('Cliente não encontrado')

    @validates('endereco_id')
    def validate_endereco_entrega(self, value):
        """
        Valida existência do endereço
        :param value: valor do atributo endereco_entrega
        :return: nulo ou ValidationError
        """
        try:
            Endereco.by_hash_id(self.context['user'].empresa_id, value)
        except HTTPForbidden as err:
            raise ValidationError('Endereço não encontrado')

    # todo: validar se endereço pertence ao cliente informado
