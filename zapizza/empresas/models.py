from pyramid.httpexceptions import HTTPNotFound
from pyramid.security import Allow, Everyone, Deny, ALL_PERMISSIONS
from sqlalchemy import (
    Column,
    Integer,
    String,
    or_
)
from sqlalchemy.orm import relationship
from pyramid_sqlalchemy import BaseObject, Session

from ..columns import ArrayType
from ..site.hashid import generate_hash, decode_hash

# Modelo da empresa
class Empresa(BaseObject):
    __tablename__ = 'empresas'
    id = Column(Integer, primary_key=True)
    hash_id = Column(String(50), index=True, unique=True)
    razao_social = Column(String(100))

    users = relationship('User', back_populates='empresa', cascade='all, delete')
    tamanhos = relationship('Tamanho', back_populates='empresa', cascade='all, delete')

    # método busca usuario por razao
    @classmethod
    def by_razao(cls, razao):
        return Session.query(cls).filter(cls.razao_social == razao).first()

# dados exemplo
sample_empresas = [
    dict(
        id=1,
        razao_social='Almir Delivery'
    ),
    dict(
        id=2,
        razao_social='Pizzaria da Nona'
    )
]