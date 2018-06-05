from pyramid.httpexceptions import HTTPNotFound
from pyramid.security import Allow, Everyone
from sqlalchemy import (
    Column,
    String,
    Integer,
    or_,
    DateTime
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.functions import now
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
    register_date = Column(DateTime, nullable=False, default=now())
    register_confirm = Column(DateTime)
    groups = Column(ArrayType)
    # todos = relationship('ToDo', backref='todos',
    #                     cascade='all, delete, delete-orphan')

    # permissões para admins. todo: users(para crud geral)
    __acl__ = [
        (Allow, 'group:admins', 'super'),
        (Allow, 'group:users', 'edit'),
        (Allow, Everyone, 'view')  # todo: tirar permissao view para todos
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


""" 
A factory do usuário obtem os dados da url da rota. Exemplo /users/{username}/edit
Quando não existe o parâmetro {username} uma instância vazia de User é retornada
Quando o parâmetro {username} existe e o usuário existe a instância de User desse username é retornada
Quando o parâmetro {username} existe e o usuário não existe retorna página não encontrada
"""


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
        email='edgar@zapizza.com.br',
        username='user',
        password='user',
        first_name='Edgar',
        last_name='Zoreia',
        groups=['group:users']
    ),
    dict(
        id=2,
        email='boco@zapizza.com.br',
        username='user1',
        password='user1',
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
        groups=['group:admins', 'group:users']
    )
]
