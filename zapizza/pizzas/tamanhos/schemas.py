from marshmallow import (
    Schema,
    fields,
    post_load,
    ValidationError,
    validates,
    validate
)
from .models import Tamanho


class TamanhoSchema(Schema):
    hash_id = fields.String()
    descricao = fields.Str(required=True, validate=validate.Length(min=3, max=120))
    sigla = fields.Str(required=True, validate=validate.Length(min=1, max=3))
    quantSabores = fields.Integer(required=True, validate=validate.Range(min=1), attribute="quant_sabores")
    quantBordas = fields.Integer(required=True, validate=validate.Range(min=0), attribute="quant_bordas")
    quantFatias = fields.Integer(required=True, validate=validate.Range(min=1), attribute="quant_fatias")
    ativo = fields.Boolean()

    # definição do objeto de retorno pos serialização
    @post_load
    def make_tamanho(self, data):
        return Tamanho(**data)

    # verificação de descrição já utilizada
    @validates('descricao')
    def validate_descricao(self, value):
        if self.context['tamanho'].descricao != value:
            if Tamanho.by_descricao(self.context['user'].empresa_id, value):
                raise ValidationError('O tamanho ' + value + ' já existe')
