from marshmallow import (
    Schema,
    fields,
    post_load,
    ValidationError,
    validates,
    validate
)
from .models import Endereco


class EnderecoSchema(Schema):
    hash_id = fields.String()
    cep = fields.Str(required=True, validate=validate.Length(equal=8))
    logradouro = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    numero = fields.Str()
    complemento = fields.Str()
    bairro = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    cidade = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    estado = fields.Str(required=True, validate=validate.Length(equal=2))


    @post_load
    def make_endereco(self, data):
        """
        :param data: dados do objeto a ser deserializado
        :return: instância de Endereco
        """
        return Endereco(**data)

    @validates('logradouro')
    def validate_logradouro(self, value):
        """
        Verifica se cliente já possui o logradouro cadastrado
        :param value: valor do atributo logradouro
        :return: nulo ou ValidationError
        """
        if self.context['endereco'].logradouro != value:
            if Endereco.by_logradouro(self.context['cliente_id'], value):
                raise ValidationError('O cliente já possui endereço no logradouro informado')
