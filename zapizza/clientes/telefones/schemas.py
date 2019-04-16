from marshmallow import (
    Schema,
    fields,
    post_load,
    post_dump,
    ValidationError,
    validates,
    validate
)
from .models import Telefone
from ...site.hashid import get_decoded_id, generate_hash


class TelefoneSchema(Schema):
    hash_id = fields.String()
    telefone = fields.Str(required=True, validate=validate.Length(min=10, max=11))
    tipo = fields.Str(required=True, validate=validate.OneOf(['Celular', 'Casa', 'Trabalho']))

    @post_load
    def make_telefone(self, data):
        """
        :param data: dados do objeto a ser deserializado
        :return: instância de Telefone
        """
        t = Telefone(**data)
        if t.hash_id:
            decoded_id = get_decoded_id('telefones', t.hash_id, self.context['user'].empresa_id)
            t.id = decoded_id
        else:
            # hash_id em inserções precisa ser nulo e não vazio
            t.hash_id = None
        return t

    @validates('telefone')
    def validate_telefone(self, value):
        """
        Verifica se cliente já possui o telefone cadastrado
        :param value: valor do atributo telefone
        :return: nulo ou ValidationError
        """
        if 'telefone' in self.context and self.context['telefone'] != value:
            if Telefone.by_telefone(self.context['cliente_id'], value):
                raise ValidationError('O cliente já possui o telefone ' + value + ' cadastrado')
