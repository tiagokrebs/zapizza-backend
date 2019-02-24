from marshmallow import (
    Schema,
    fields,
    post_load,
    post_dump,
    ValidationError,
    validates,
    validate
)
from .models import Sabor, SaborTamanho
from ..tamanhos.models import Tamanho
from ...site.hashid import generate_hash


class SaborTamanhoSchema(Schema):
    """
        Classe filho tamanho

        Possui métodos para tradução de id/hash_id na serialização/deserialização
        A api não deve nunca retornar o id que consta no banco de dados
    """
    hash_id = fields.String(attribute="tamanho_id")
    valor = fields.Number()

    @post_load
    def make_sabor_tamanho(self, data):
        """
        No pós deserialização objeto SaborTamanho é composto
        onde atributo 'tamanho' recebe objeto Tamanho referente ao hash_id
        e valor de 'tamanho_id' é alterado de hash_id para id

        :param data: dados do objeto a ser deserializado
        :return: instância de SaborTamanho
        """
        t = Tamanho.by_hash_id(self.context['user'].empresa_id, data['tamanho_id'])
        data['tamanho'] = t
        data['tamanho_id'] = t.id
        return SaborTamanho(**data)

    @post_dump(pass_many=True)
    def encode_id(self, data, many):
        """
        No pós serialização id é codificado para hash_id

        :param data: dados do objeto a ser serializadp
        :param many: true/false indica se objeto é uma lista
        :return: dados com id codificado
        """
        for d in data:
            encoded_id = generate_hash('tamanhos', [self.context['user'].empresa_id, int(d['hash_id'])])
            d['hash_id'] = encoded_id
        return data


class SaborSchema(Schema):
    """
        Classe principal do sabor integra tamanhos como filhos de sabor
    """
    hash_id = fields.String()
    descricao = fields.Str(required=True, validate=validate.Length(min=3, max=120))
    ativo = fields.Boolean()
    tamanhos = fields.Nested(SaborTamanhoSchema, required=True, many=True)

    @post_load
    def make_sabor(self, data):
        """
        :param data: dados do objeto a ser deserializado
        :return: instância de Sabor
        """
        return Sabor(**data)

    @validates('descricao')
    def validate_descricao(self, value):
        """
        Valiação se descrição do sabor já é utilizada por outro objeto

        :param value: valor do atributo de descrição
        :return: nulo ou ValidationError
        """
        if self.context['sabor'].descricao != value:
            if Sabor.by_descricao(self.context['user'].empresa_id, value):
                raise ValidationError('O sabor ' + value + ' já existe')
