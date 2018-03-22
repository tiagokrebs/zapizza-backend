from pyramid.httpexceptions import HTTPNotFound
from pyramid.security import Allow, Everyone
from sqlalchemy import (
    Column,
    String,
    Integer
)
from sqlalchemy.orm import relationship, backref
from pyramid_sqlalchemy import BaseObject, Session

# SQLite doesn't support arrays, workaround
from ..columns import ArrayType

# todo: inserir telefone do usuário
class User(BaseObject):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(120), unique=True)
    password = Column(String(120))
    first_name = Column(String(120))
    last_name = Column(String(120))
    groups = Column(ArrayType)
    todos = relationship('ToDo', backref='todos',
                         cascade='all, delete, delete-orphan')

    __acl__ = [
        (Allow, 'group:admins', 'view'),
        (Allow, 'group:admins', 'edit')
    ]

    @property
    def title(self):
        return '%s %s' % (self.first_name, self.last_name)

    @classmethod
    def by_username(cls, username):
        return Session.query(cls).filter(cls.username == username).first()

    @classmethod
    def list(cls):
        return Session.query(cls).order_by(cls.last_name)


def user_factory(request):
    username = request.matchdict.get('username')
    if username is None:
        # Return the class
        return User
    user = User.by_username(username)
    if not user:
        raise HTTPNotFound()
    return user


sample_users = [
    dict(
        id=1,
        username='editor',
        password='editor',
        first_name='Ed',
        last_name='Bota',
        groups=['group:editors']
    ),
    dict(
        id=2,
        username='user',
        password='user',
        first_name='Bocó',
        last_name='de Mola',
        groups=[]
    ),
    dict(
        id=3,
        username='admin',
        password='admin',
        first_name='Yoda',
        last_name='Mestre',
        groups=['group:admins', 'group:editors']
    )
]
