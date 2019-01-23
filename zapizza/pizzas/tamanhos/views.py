from pyramid.httpexceptions import (
    HTTPFound,
    HTTPOk,
    HTTPNotFound
)
from pyramid.view import (
    view_config,
    view_defaults
)
from deform import Form, ValidationFailure
from pyramid_sqlalchemy import Session
from .models import Tamanho
from ...site.hashid import generate_hash
from .schemas import TamanhoSchema
from json import dumps
from marshmallow.utils import is_iterable_but_not_string


@view_defaults(permission='super')
class TamanhoViews:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.current_user = request.user

    @view_config(route_name='tamanhos', renderer='json',
                 request_method='GET')
    def tamanhos_list(self):
        tamanhos = Tamanho.list(self.current_user.empresa_id)
        schema = TamanhoSchema(many=is_iterable_but_not_string(tamanhos), strict=True)
        result = schema.dump(tamanhos)

        if tamanhos:
            res = dumps(dict(
                data=dict(
                    code=200,
                    tamanhos=result.data)),
                ensure_ascii=False)
            return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

        msg = 'Nenhum registro encontrado'
        res = dumps(dict(error=dict(code=404, message=msg)), ensure_ascii=False)
        return HTTPNotFound(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='tamanhos', renderer='json',
                 request_method='POST')
    def tamanho_add(self):
        tamanho_schema = TamanhoSchema()
        controls = self.request.POST.items()
        edit_form = Form(tamanho_schema)
        try:
            appstruct = edit_form.validate(controls)
        except ValidationFailure as e:
            # o formulário não é válido
            edit_form.set_appstruct(e.cstruct)
            return dict(edit_form=edit_form)

        # o formulário é valido
        descricao = appstruct['descricao']
        sigla = appstruct['sigla']
        quant_sabores = appstruct['quant_sabores']
        quant_bordas = appstruct['quant_bordas']
        quant_fatias = appstruct['quant_fatias']
        t = Tamanho(
            descricao=descricao, sigla=sigla,
            quant_sabores=quant_sabores,
            quant_bordas=quant_bordas,
            quant_fatias=quant_fatias,
            ativo=True,
            empresa_id=self.current_user.empresa_id
        )
        Session.add(t)
        Session.flush()
        Session.refresh(t)
        t.hash_id = generate_hash('tamanhos', [self.current_user.empresa_id, t.id])

        self.request.session.flash('Inserido: %s' % t.descricao, 'primary')
        return HTTPFound(location=self.request.route_url('tamanhos_list'))

    @view_config(route_name='tamanhos_edit', renderer='json',
                 request_method='GET')
    def tamanho_get(self):
        tamanho_schema = TamanhoSchema()
        edit_form = Form(tamanho_schema)
        edit_form.set_appstruct(dict(
            descricao=self.context.descricao,
            sigla=self.context.sigla,
            quant_sabores=self.context.quant_sabores,
            quant_bordas=self.context.quant_bordas,
            quant_fatias=self.context.quant_fatias
        ))
        return dict(edit_form=edit_form)

    @view_config(route_name='tamanhos_edit', renderer='json',
                 request_method='PUT')
    def tamanho_update(self):
        tamanho_schema = TamanhoSchema()
        controls = self.request.POST.items()
        edit_form = Form(tamanho_schema)
        try:
            appstruct = edit_form.validate(controls)
        except ValidationFailure as e:
            # o formulário não é válido
            edit_form.set_appstruct(e.cstruct)
            return dict(edit_form=edit_form)

        # o formulário é valido
        self.context.descricao = appstruct['descricao']
        self.context.sigla = appstruct['sigla']
        self.context.quant_sabores = appstruct['quant_sabores']
        self.context.quant_bordas = appstruct['quant_bordas']
        self.context.quant_fatias = appstruct['quant_fatias']

        self.request.session.flash('Alteração realizada: %s' % self.context.descricao, 'primary')
        return HTTPFound(location=self.request.route_url('tamanhos_list'))

    @view_config(route_name='tamanhos_enable', request_method='PUT',
                 renderer='json')
    def tamanho_enable(self):
        self.context.ativo = True
        self.request.session.flash('Ativado: %s' % self.context.descricao, 'success')
        return HTTPFound(location=self.request.route_url('tamanhos_list'))
