from marshmallow import (
    Schema,
    fields,
    post_load,
    ValidationError,
    validates,
    validate
)
from .models import Cliente
from .telefones.schemas import TelefoneSchema
from .enderecos.schemas import EnderecoSchema


class ClienteSchema(Schema):
    hash_id = fields.String()
    nome = fields.Str(required=True, validate=validate.Length(min=3, max=120))
    ativo = fields.Boolean()
    telefones = fields.Nested(TelefoneSchema, required=True, many=True)
    enderecos = fields.Nested(EnderecoSchema, required=True, many=True)

    @post_load
    def make_cliente(self, data):
        """
        :param data: dados do objeto a ser deserializado
        :return: instância de Cliente
        """
        return Cliente(**data)


class ClienteSelectSchema(Schema):
    hash_id = fields.String(dump_to='value')
    nome = fields.Str(dump_to='label')
    telefone = fields.Str(dump_to='label')
