from marshmallow import (
    Schema,
    fields,
    post_load,
    ValidationError,
    validates,
    validate
)
from .models import Cliente


class ClienteSchema(Schema):
    hash_id = fields.String()
    nome = fields.Str(required=True, validate=validate.Length(min=3, max=120))
    ativo = fields.Boolean()

    @post_load
    def make_cliente(self, data):
        """
        :param data: dados do objeto a ser deserializado
        :return: instância de Cliente
        """
        return Cliente(**data)
