from pyramid.httpexceptions import HTTPFound
from pyramid.view import (
    view_config,
    view_defaults
)

import colander
from deform import Form, ValidationFailure

from pyramid_sqlalchemy import Session

from ..pizzas.models import Borda


class BordaSchema(colander.MappingSchema):
    nome_borda = colander.SchemaNode(colander.String())
    valor_borda = colander.SchemaNode(colander.String())


@view_defaults(permission='view')
class BordaViews:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.schema = BordaSchema()
        self.form = Form(self.schema, buttons=('submit',))

    @view_config(route_name='bordas_list',
                 renderer='templates/list.jinja2'
                 )
    def list(self):
        return dict(bordas=Borda.list())

    @view_config(route_name='bordas_add',
                 renderer='templates/add.jinja2',
                 request_method='POST')
    def add_handler(self):
        controls = self.request.POST.items()
        try:
            appstruct = self.form.validate(controls)
        except ValidationFailure as e:
            # Formulatio NAO é valido
            return dict(add_form=e.render())

        # adiciona uma nova borda ao banco e redireciona
        nome_borda = appstruct['nome_borda']
        valor_borda = appstruct['valor_borda']
        Session.add(Borda(
            nome_borda=nome_borda, valor_borda=valor_borda
        ))
        borda = Borda.by_nome_borda(nome_borda)
        self.request.session.flash('Adicionada: %s' % borda.nome_borda)
        url = self.request.route_url('bordas_list', id=borda.id)
        return HTTPFound(url)

    @view_config(route_name='bordas_view',
                 permission='view',
                 renderer='templates/view.jinja2')
    def view(self):
        return dict()

    @view_config(route_name='bordas_edit',
                 renderer='templates/edit.jinja2')
    def edit(self):
        edit_form = self.form.render(dict(
            nome_borda=self.context.nome_borda,
            valor_borda=self.context.valor_borda
        ))
        return dict(edit_form=edit_form)

    @view_config(route_name='bordas_edit',
                 renderer='templates/edit.jinja2',
                 request_method='POST')
    def edit_handler(self):
        controls = self.request.POST.items()
        try:
            appstruct = self.form.validate(controls)
        except ValidationFailure as e:
            # Formulário não é valido
            return dict(edit_form=e.render())

        # Formulário válido então salva dado e envia mensagem
        self.context.nome_borda = appstruct['nome_borda']
        self.context.valor_borda = appstruct['valor_borda']
        self.request.session.flash('Alterada: %s' % self.context.nome_borda)
        url = self.request.route_url('bodas_view',
                                     id=self.context.id)
        return HTTPFound(url)

    @view_config(route_name='bordas_delete')
    def delete(self):
        msg = 'Deleted: %s' % self.context.nome_borda
        self.request.session.flash('Deleted: %s' % self.context.nome_borda)
        Session.delete(self.context)
        url = self.request.route_url('bordas_list', _query=dict(msg=msg))
        return HTTPFound(url)
