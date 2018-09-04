from pyramid.httpexceptions import HTTPFound
from pyramid.view import (
    view_config,
    view_defaults
)

import colander
from deform import Form, ValidationFailure

from pyramid_sqlalchemy import Session

from ..todos.models import ToDo
from ..users.models import User


class ToDoSchema(colander.MappingSchema):
    title = colander.SchemaNode(colander.String())


@view_defaults(permission='edit')
class ToDoViews:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.schema = ToDoSchema()
        self.form = Form(self.schema, buttons=('submit',))
        self.messages = request.session.pop_flash()
        self.current_user = User.by_username(request.authenticated_userid)

    @view_config(route_name='todos_list',
                 renderer='templates/list.jinja2',
                 permission='view')
    def list(self):
        return dict(todos=ToDo.list())

    @view_config(route_name='todos_add', renderer='templates/add.jinja2')
    def add(self):
        return dict(add_form=self.form.render())

    @view_config(route_name='todos_add',
                 renderer='templates/add.jinja2',
                 request_method='POST')
    def add_handler(self):
        controls = self.request.POST.items()
        try:
            appstruct = self.form.validate(controls)
        except ValidationFailure as e:
            # Form is NOT valid
            return dict(add_form=e.render())

        # Add a new to do to the database then redirect
        title = appstruct['title']
        Session.add(ToDo(title=title, owner=self.current_user))
        todo = Session.query(ToDo).filter_by(title=title).one()
        self.request.session.flash('Added: %s' % todo.id)
        url = self.request.route_url('todos_list', id=todo.id)
        return HTTPFound(url)

    @view_config(route_name='todos_view',
                 permission='view',
                 renderer='templates/view.jinja2')
    def view(self):
        return dict()

    @view_config(route_name='todos_edit',
                 renderer='templates/edit_profile.jinja2')
    def edit(self):
        edit_form = self.form.render(dict(title=self.context.title))
        return dict(edit_form=edit_form)

    @view_config(route_name='todos_edit',
                 renderer='templates/edit_profile.jinja2',
                 request_method='POST')
    def edit_handler(self):
        controls = self.request.POST.items()
        try:
            appstruct = self.form.validate(controls)
        except ValidationFailure as e:
            # Form is NOT valid
            return dict(edit_form=e.render())

        # Valid form so save the title and flash message
        self.context.title = appstruct['title']
        self.request.session.flash('Changed: %s' % self.context.id)
        url = self.request.route_url('todos_view', id=self.context.id)
        return HTTPFound(url)

    @view_config(route_name='todos_delete')
    def delete(self):
        msg = 'Deleted: %s' % (self.context.id)
        self.request.session.flash('Deleted: %s' % self.context.id)
        Session.delete(self.context)
        url = self.request.route_url('todos_list', _query=dict(msg=msg))
        return HTTPFound(url)
