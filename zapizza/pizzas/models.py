from pyramid.httpexceptions import HTTPNotFound
from pyramid.security import Allow, Everyone
from sqlalchemy import (
    Column,
    String,
    Integer,
    Numeric
)
from sqlalchemy.orm import relationship, backref
from pyramid_sqlalchemy import BaseObject, Session

# SQLite doesn't support arrays, workaround
from ..columns import ArrayType


# classe Borda
class Borda(BaseObject):
    __tablename__ = 'bordas'
    id = Column(Integer, primary_key=True)
    nome_borda = Column(String(50), nullable=False)
    valor_borda = Column(Numeric(precision=8, scale=2), nullable=False)

    # permissoes default
    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, 'group:editors', 'edit')
    ]

    # metodo retorna borda por nome_borda
    @classmethod
    def by_nome_borda(cls, nome_borda):
        return Session.query(cls).filter(cls.nome_borda == nome_borda)

    # metodo retorna lista de nomes das bordas
    @classmethod
    def list(cls):
        return Session.query(cls).order_by(cls.nome_borda)


def borda_factory(request):
    borda_id = request.matchdict.get('id')
    if borda_id is None:
        # Return the class
        return Borda
    borda_id_int = int(borda_id)
    borda = Session.query(Borda).filter_by(id=borda_id_int).first()
    if not borda:
        raise HTTPNotFound()
    return borda


sample_bordas = [
    dict(
        id=1,
        nome_borda='Queijo cheddar',
        valor_borda=3.00
    ),
    dict(
        nome_borda='Doce de Leite',
        valor_borda=3.00
    )
]


# classe Bebida
class Bebida(BaseObject):
    __tablename__ = 'bebidas'
    id = Column(Integer, primary_key=True)
    nome_bebida = Column(String(50), nullable=False)
    valor_bebida = Column(Numeric(precision=8, scale=2), nullable=False)

    # permissoes default
    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, 'group:editors', 'edit')
    ]

    # metodo retorna bebida por id
    @classmethod
    def by_id(cls, id):
        return Session.query(cls).filter(cls.id)

    # metodo retorna lista de nomes das bebidas
    @classmethod
    def list(cls):
        return Session.query(cls).order_by(cls.nome_bebida)


def bebida_factory(request):
    bebida_id = request.matchdict.get('id')
    if bebida_id is None:
        # Return the class
        return Bebida
    bebida_id_int = int(bebida_id)
    bebida = Session.query(Bebida).filter_by(id=bebida_id_int).first()
    if not bebida:
        raise HTTPNotFound()
    return bebida


sample_bebidas = [
    dict(
        id=1,
        nome_bebida='Coca-cola 2l',
        valor_bebida=5.00
    ),
    dict(
        id=2,
        nome_bebida='Guaraná 2l',
        valor_bebida=4.00
    ),
    dict(
        id=3,
        nome_bebida='Fanta Uva 2l',
        valor_bebida=4.50
    )
]
