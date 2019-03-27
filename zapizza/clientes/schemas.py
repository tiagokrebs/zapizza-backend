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

    # todo: para evitar que telefones e endereços sofram delete e insert adicionar cliente_id aos objetos filho

    @post_load
    def make_cliente(self, data):
        """
        :param data: dados do objeto a ser deserializado
        :return: instância de Cliente
        """
        return Cliente(**data)
