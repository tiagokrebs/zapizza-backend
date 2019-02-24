from marshmallow import (
    Schema,
    fields,
    post_load,
    ValidationError,
    validates,
    validate
)
from .models import Bebida


class BebidaSchema(Schema):
    hash_id = fields.String()
    descricao = fields.Str(required=True, validate=validate.Length(min=3, max=120))
    ativo = fields.Boolean()
    valor = fields.Number(required=True)

    @post_load
    def make_bebida(self, data):
        """
        :param data: dados do objeto a ser deserializado
        :return: instância de Bebida
        """
        return Bebida(**data)

    @validates('descricao')
    def validate_descricao(self, value):
        """
        Validação se descrição da bebida já é utilizada por outro objeto
        :param value: valor do atributo descrição
        :return: nulo ou ValidationError
        """
        if self.context['bebida'].descricao != value:
            if Bebida.by_descricao(self.context['user'].empresa_id, value):
                raise ValidationError('A bebida ' + value + ' já existe')
