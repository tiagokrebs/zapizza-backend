import colander
from marshmallow import Schema, fields


class TamanhoSchema(Schema):
    id = fields.Integer()
    descricao = fields.Str()
    sigla = fields.Str()
    quantSabores = fields.Integer(attribute="quant_sabores")
    quantBordas = fields.Integer(attribute="quant_bordas")
    quantFatias = fields.Integer(attribute="quant_fatias")
    ativo = fields.Boolean()

# class TamanhoSchema(colander.MappingSchema):
#     descricao = colander.SchemaNode(colander.String(),
#                                     name='descricao', missing=colander.required,
#                                     missing_msg='Campo obrigatório',
#                                     validator=colander.Length(min=3, max=120,
#                                                               min_err='Informe no mínimo 3 caracteres',
#                                                               max_err='Informe no máximo 120 caracteres'),
#                                     title='Descrição', description='Tamanho da pizza'
#                                     )
#     sigla = colander.SchemaNode(colander.String(),
#                                 name='sigla', missing=colander.required,
#                                 missing_msg='Campo obrigatório',
#                                 validator=colander.Length(max=3,
#                                                           max_err='Informe no máximo 3 caracteres'),
#                                 title='Sigla', description='Sigla do tamanho'
#                                 )
#     quant_sabores = colander.SchemaNode(colander.Integer(),
#                                         name='quant_sabores', missing=colander.required,
#                                         missing_msg='Campo obrigatório',
#                                         validator=colander.Range(min=1, max=99,
#                                                                  min_err='A quantidade mínima de sabores é 1',
#                                                                  max_err='A quanidade máxima de sabores é 99'),
#                                         title='Quantidade de sabores', description='Quantidade de sabores do tamanho'
#                                         )
#     quant_bordas = colander.SchemaNode(colander.Integer(),
#                                        name='quant_bordas', missing=colander.required,
#                                        missing_msg='Campo obrigatório',
#                                        validator=colander.Range(min=0, max=99,
#                                                                 min_err='A quantidade mínima de sabores é 0',
#                                                                 max_err='A quanidade máxima de sabores é 99'),
#                                        title='Quantidade de bordas', description='Quantidade de bordas do tamanho'
#                                        )
#     quant_fatias = colander.SchemaNode(colander.Integer(),
#                                        name='quant_fatias', missing=colander.null,
#                                        validator=colander.Range(min=1, max=99,
#                                                                 min_err='A quantidade mínima de fatias é 1',
#                                                                 max_err='A quantidade máxima de fatias é 1'),
#                                        title='Quantidade de fatias', description='Quantidade de fatias do tamanho'
#                                        )
