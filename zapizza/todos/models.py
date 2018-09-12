from pyramid.httpexceptions import HTTPNotFound
from pyramid.security import Allow, Everyone
from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey
)
from sqlalchemy.orm import relationship
from pyramid_sqlalchemy import BaseObject, Session

from ..columns import ArrayType


class ToDo(BaseObject):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True)
    title = Column(Text)
    acl = Column(ArrayType)

    # acl a nivel de objeto
    # permissoes diferentes para registros diferentes no bd
    default_acl = [
        (Allow, Everyone, 'view'),
        (Allow, 'group:editors', 'edit')
    ]

    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship('User')
    # acl a nivel de objeto
    def __acl__(self=None):
        return getattr(self, 'acl', None) or ToDo.default_acl

    @classmethod
    def by_id(cls, todo_id):
        # Do an int() just in case '1' was passed in
        return Session.query(cls).filter_by(id=int(todo_id)).first()

    @classmethod
    def list(cls):
        return Session.query(cls).order_by(cls.title)


def todo_factory(request):
    todo_id = request.matchdict.get('id')
    if todo_id is None:
        # Return the class
        return ToDo
    todo = ToDo.by_id(int(todo_id))
    if not todo:
        raise HTTPNotFound()
    return todo


sample_todos = [
    dict(title='Get Milk'),
    dict(title='Get Eggs'),
    dict(title='Secure Task',
         acl=[
             ('Allow', 'group:admins', 'view'),
             ('Allow', 'group:admins', 'edit')
         ]
         )
]
