from marshmallow import (
    Schema,
    fields,
    post_load,
    ValidationError,
    validates,
    validate
)
from .models import Telefone


class TelefoneSchema(Schema):
    hash_id = fields.String()
    telefone = fields.Str(required=True, validate=validate.Length(min=8, max=15))

    @post_load
    def make_telefone(self, data):
        """
        :param data: dados do objeto a ser deserializado
        :return: instância de Telefone
        """
        return Telefone(**data)

    @validates('telefone')
    def validate_telefone(self, value):
        """
        Verifica se cliente já possui o telefone cadastrado
        :param value: valor do atributo telefone
        :return: nulo ou ValidationError
        """
        if self.context['telefone'] != value:
            if Telefone.by_telefone(self.context['cliente_id'], value):
                raise ValidationError('O cliente já possui o telefone ' + value + ' cadastrado')
