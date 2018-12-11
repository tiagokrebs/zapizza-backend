from pyramid.httpexceptions import HTTPFound
from pyramid.view import (
    view_config,
    view_defaults
)
import colander
from deform import Form, ValidationFailure
from pyramid_sqlalchemy import Session
from ..users.models import User
from ..pizzas.models import (
    Tamanho,
    Sabor
)
from pyramid.security import remember
from ..site.hashid import generate_hash


class TamanhoSchema(colander.MappingSchema):
    descricao = colander.SchemaNode(colander.String(),
                                    name='descricao', missing=colander.required,
                                    missing_msg='Campo obrigatório',
                                    validator=colander.Length(min=3, max=120,
                                                              min_err='Informe no mínimo 3 caracteres',
                                                              max_err='Informe no máximo 120 caracteres'),
                                    title='Descrição', description='Tamanho da pizza'
                                    )
    sigla = colander.SchemaNode(colander.String(),
                                name='sigla', missing=colander.required,
                                missing_msg='Campo obrigatório',
                                validator=colander.Length(max=3,
                                                          max_err='Informe no máximo 3 caracteres'),
                                title='Sigla', description='Sigla do tamanho'
                                )
    quant_sabores = colander.SchemaNode(colander.Integer(),
                                        name='quant_sabores', missing=colander.required,
                                        missing_msg='Campo obrigatório',
                                        validator=colander.Range(min=1, max=99,
                                                                 min_err='A quantidade mínima de sabores é 1',
                                                                 max_err='A quanidade máxima de sabores é 99'),
                                        title='Quantidade de sabores', description='Quantidade de sabores do tamanho'
                                        )
    quant_bordas = colander.SchemaNode(colander.Integer(),
                                       name='quant_bordas', missing=colander.required,
                                       missing_msg='Campo obrigatório',
                                       validator=colander.Range(min=0, max=99,
                                                                min_err='A quantidade mínima de sabores é 0',
                                                                max_err='A quanidade máxima de sabores é 99'),
                                       title='Quantidade de bordas', description='Quantidade de bordas do tamanho'
                                       )
    quant_fatias = colander.SchemaNode(colander.Integer(),
                                       name='quant_fatias', missing=colander.null,
                                       validator=colander.Range(min=1, max=99,
                                                                min_err='A quantidade mínima de fatias é 1',
                                                                max_err='A quantidade máxima de fatias é 1'),
                                       title='Quantidade de fatias', description='Quantidade de fatias do tamanho'
                                       )


class SaborSchema(colander.MappingSchema):
    descricao = colander.SchemaNode(colander.String(),
                                    name='descricao', missing=colander.required,
                                    missing_msg='Campo obrigatório',
                                    validator=colander.Length(min=3, max=120,
                                                              min_err='Informe no mínimo 3 caracteres',
                                                              max_err='Informe no máximo 120 caracteres'),
                                    title='Descrição', description='Sabor da pizza'
                                    )


@view_defaults(permission='view')
class TamanhoViews:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.primary_messages = request.session.pop_flash('primary')
        self.success_messages = request.session.pop_flash('success')
        self.danger_messages = request.session.pop_flash('danger')
        self.warning_messages = request.session.pop_flash('warning')
        self.current_user = User.by_username(request.authenticated_userid)

    @view_config(route_name='tamanhos_list',
                 renderer='templates/tamanho/list.jinja2'
                 )
    def list(self):
        return dict(primary_messages=self.primary_messages,
                    success_messages=self.success_messages,
                    danger_messages=self.danger_messages,
                    warning_messages=self.warning_messages,
                    tamanhos=Tamanho.list(self.current_user.empresa_id))

    @view_config(route_name='tamanhos_disable',
                 renderer='templates/tamanho/list.jinja2')
    def enable_hanlder(self):
        self.context.ativo = False
        self.request.session.flash('Desativado: %s' % self.context.descricao, 'warning')
        return HTTPFound(location=self.request.route_url('tamanhos_list'))

    @view_config(route_name='tamanhos_enable',
                 renderer='templates/tamanho/list.jinja2')
    def disable_hanlder(self):
        self.context.ativo = True
        self.request.session.flash('Ativado: %s' % self.context.descricao, 'success')
        return HTTPFound(location=self.request.route_url('tamanhos_list'))

    @view_config(route_name='tamanhos_edit',
                 renderer='templates/tamanho/edit.jinja2')
    def edit(self):
        tamanho_schema = TamanhoSchema().bind()
        edit_form = Form(tamanho_schema)
        edit_form.set_appstruct(dict(
            descricao=self.context.descricao,
            sigla=self.context.sigla,
            quant_sabores=self.context.quant_sabores,
            quant_bordas=self.context.quant_bordas,
            quant_fatias=self.context.quant_fatias
        ))
        return dict(edit_form=edit_form)

    @view_config(route_name='tamanhos_edit',
                 renderer='templates/tamanho/edit.jinja2',
                 request_method='POST')
    def edit_handler(self):
        tamanho_schema = TamanhoSchema().bind()
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

    @view_config(route_name='tamanhos_add',
                 renderer='templates/tamanho/edit.jinja2')
    def add(self):
        tamanho_schema = TamanhoSchema().bind()
        edit_form = Form(tamanho_schema)
        return dict(edit_form=edit_form)

    @view_config(route_name='tamanhos_add',
                 renderer='templates/tamanho/edit.jinja2',
                 request_method='POST')
    def add_handler(self):
        tamanho_schema = TamanhoSchema().bind()
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


@view_defaults(permission='view')
class SaborViews:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.primary_messages = request.session.pop_flash('primary')
        self.success_messages = request.session.pop_flash('success')
        self.danger_messages = request.session.pop_flash('danger')
        self.warning_messages = request.session.pop_flash('warning')
        self.current_user = User.by_username(request.authenticated_userid)

    @view_config(route_name='sabores_list',
                 renderer='templates/sabor/list.jinja2')
    def list(self):
        lista = Sabor.list(self.current_user.empresa_id)
        return dict(primary_messages=self.primary_messages,
                    success_messages=self.success_messages,
                    danger_messages=self.danger_messages,
                    warning_messages=self.warning_messages,
                    sabores=Sabor.list(self.current_user.empresa_id))

    @view_config(route_name='sabores_disable',
                 renderer='templates/sabor/list.jinja2')
    def enable_hanlder(self):
        self.context.ativo = False
        self.request.session.flash('Desativado: %s' % self.context.descricao, 'warning')
        return HTTPFound(location=self.request.route_url('sabores_list'))

    @view_config(route_name='sabores_enable',
                 renderer='templates/sabor/list.jinja2')
    def disable_hanlder(self):
        self.context.ativo = True
        self.request.session.flash('Ativado: %s' % self.context.descricao, 'success')
        return HTTPFound(location=self.request.route_url('sabores_list'))

    @view_config(route_name='sabores_edit',
                 renderer='templates/sabor/edit.jinja2')
    def edit(self):
        sabor_schema = SaborSchema().bind()
        edit_form = Form(sabor_schema)
        edit_form.set_appstruct(dict(
            descricao=self.context.descricao
        ))
        return dict(edit_form=edit_form)

    @view_config(route_name='sabores_edit',
                 renderer='templates/sabor/edit.jinja2',
                 request_method='POST')
    def edit_handler(self):
        sabor_schema = SaborSchema().bind()
        controls = self.request.POST.items()
        edit_form = Form(sabor_schema)
        try:
            appstruct = edit_form.validate(controls)
        except ValidationFailure as e:
            # o formulário não é válido
            edit_form.set_appstruct(e.cstruct)
            return dict(edit_form=edit_form)

        # o formulário é valido
        self.context.descricao = appstruct['descricao']

        self.request.session.flash('Alteração realizada: %s' % self.context.descricao, 'primary')
        return HTTPFound(location=self.request.route_url('sabores_list'))

    @view_config(route_name='sabores_add',
                 renderer='templates/sabor/edit.jinja2')
    def add(self):
        sabor_schema = SaborSchema().bind()
        edit_form = Form(sabor_schema)
        return dict(edit_form=edit_form)

    @view_config(route_name='sabores_add',
                 renderer='templates/sabor/edit.jinja2',
                 request_method='POST')
    def add_handler(self):
        sabor_schema = SaborSchema().bind()
        controls = self.request.POST.items()
        edit_form = Form(sabor_schema)
        try:
            appstruct = edit_form.validate(controls)
        except ValidationFailure as e:
            # o formulário não é válido
            edit_form.set_appstruct(e.cstruct)
            return dict(edit_form=edit_form)

        # o formulário é valido
        descricao = appstruct['descricao']
        s = Sabor(
            descricao=descricao,
            ativo=True,
            empresa_id=self.current_user.empresa_id
        )
        Session.add(s)
        Session.flush()
        Session.refresh(s)
        s.hash_id = generate_hash('sabores', [self.current_user.empresa_id, s.id])

        self.request.session.flash('Inserido: %s' % s.descricao, 'primary')
        return HTTPFound(location=self.request.route_url('sabores_list'))

