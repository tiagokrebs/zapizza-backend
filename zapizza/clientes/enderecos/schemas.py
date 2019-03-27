from marshmallow import (
    Schema,
    fields,
    post_load,
    ValidationError,
    validates,
    validate
)
from .models import Endereco
from ...site.hashid import get_decoded_id


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
        Caso hash_id exista em data é necessário definir id do objeto
        Objetos com id geram um UPDATE do banco de dados
        Objetos sem id geram INSERT
        :param data: dados do objeto a ser deserializado
        :return: instância de Endereco
        """
        e = Endereco(**data)
        if e.hash_id:
            decoded_id = get_decoded_id('enderecos', e.hash_id, self.context['user'].empresa_id)
            e.id = decoded_id
        else:
            # hash_id em inserções precisa ser nulo e não vazio
            e.hash_id = None
        return e

    @validates('logradouro')
    def validate_logradouro(self, value):
        """
        Verifica se cliente já possui o logradouro cadastrado
        :param value: valor do atributo logradouro
        :return: nulo ou ValidationError
        """
        if 'endereco' in self.context and self.context['endereco'].logradouro != value:
            if Endereco.by_logradouro(self.context['cliente_id'], value):
                raise ValidationError('O cliente já possui endereço no logradouro informado')
