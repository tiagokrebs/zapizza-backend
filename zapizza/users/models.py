from pyramid.httpexceptions import HTTPNotFound
from pyramid.security import Allow, Everyone
from sqlalchemy import (
    Column,
    String,
    Integer,
    or_
)
from sqlalchemy.orm import relationship, backref
from pyramid_sqlalchemy import BaseObject, Session

# SQLite doesn't support arrays, workaround
from ..columns import ArrayType


# Modelo do usuario
class User(BaseObject):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(150), unique=True, nullable=False)
    username = Column(String(120), unique=True, nullable=False)
    password = Column(String(120), nullable=False)
    first_name = Column(String(120))
    last_name = Column(String(120))
    groups = Column(ArrayType)
    # todos = relationship('ToDo', backref='todos',
    #                     cascade='all, delete, delete-orphan')

    __acl__ = [
        (Allow, 'group:admins', 'view'),
        (Allow, 'group:admins', 'edit')
    ]

    # propriedade com nome e sobrenome do usuário
    @property
    def title(self):
        return '%s %s' % (self.first_name, self.last_name)

    # método busca usuario por username
    @classmethod
    def by_username(cls, username):
        return Session.query(cls).filter(or_(cls.username == username, cls.email == username)).first()

    # método retorna lista de usuários ordenada nome
    @classmethod
    def list(cls):
        return Session.query(cls).order_by(cls.first_name)


# factory do usuário
def user_factory(request):
    username = request.matchdict.get('username')
    if username is None:
        # Return the class
        return User
    user = User.by_username(username)
    if not user:
        raise HTTPNotFound()
    return user


# dados exemplo para iniciação do banco de dados
sample_users = [
    dict(
        id=1,
        email='editor@zapizza.com.br',
        username='editor',
        password='editor',
        first_name='Ed',
        last_name='Bota',
        groups=['group:editors']
    ),
    dict(
        id=2,
        email='user@zapizza.com.br',
        username='user',
        password='user',
        first_name='Bocó',
        last_name='de Mola',
        groups=[]
    ),
    dict(
        id=3,
        email='admin@zapizza.com.br',
        username='admin',
        password='admin',
        first_name='Yoda',
        last_name='Mestre',
        groups=['group:admins', 'group:editors']
    )
]
