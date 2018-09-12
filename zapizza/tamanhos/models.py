from pyramid.httpexceptions import HTTPNotFound
from pyramid.security import Allow, Deny, ALL_PERMISSIONS

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    and_
)
from sqlalchemy.orm import relationship
from pyramid_sqlalchemy import BaseObject, Session
from ..site.hashid import decode_hash


class Tamanho(BaseObject):
    __tablename__ = 'tamanhos'
    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=False)
    hash_id = Column(String(50), index=True, unique=True)
    descricao = Column(String(120), nullable=False)
    sigla = Column(String(3), nullable=False)
    quant_sabores = Column(Integer, nullable=False)
    quant_bordas = Column(Integer, nullable=False)
    quant_fatias = Column(Integer)

    empresa = relationship('Empresa', back_populates='tamanhos')

    # permissões
    __acl__ = [
        (Allow, 'group:admins', 'view'),
        (Allow, 'group:editors', 'view'),
        (Allow, 'group:users', 'view'),
    ]

    @classmethod
    def by_id(cls, tamanho_id):
        return Session.query(cls).filter_by(id=int(tamanho_id))

    @classmethod
    def by_hash_id(cls, tamanho_hash_id):
        data = decode_hash('tamanhos', tamanho_hash_id)
        empresa_id = data[0]
        id = data[1]
        return Session.query(cls).filter_by(and_(id=int(id), empresa_id=int(empresa_id)))

    @classmethod
    def list(cls):
        return Session.query(cls).order_by(cls.descricao)


def tamanho_factory(request):
    tamanho_hash_id = request.matchdict.get('hashid')
    if tamanho_hash_id is None:
        # retorna a classe
        return Tamanho
    tamanho = Tamanho.by_hash_id(tamanho_hash_id)
    if not tamanho:
        raise HTTPNotFound()
    return tamanho


# dados exemplo
sample_tamanhos = [
    dict(
        id=1,
        descricao='Brotinho',
        sigla='B',
        quant_sabores=1,
        quant_bordas=1,
        quant_fatias=4
    ),
    dict(
        id=2,
        descricao='Pequena',
        sigla='P',
        quant_sabores=2,
        quant_bordas=1,
        quant_fatias=6
    ),
    dict(
        id=3,
        descricao='Média',
        sigla='M',
        quant_sabores=3,
        quant_bordas=1,
        quant_fatias=9
    ),
    dict(
        id=4,
        descricao='Grande',
        sigla='G',
        quant_sabores=4,
        quant_bordas=2,
        quant_fatias=12
    ),
    dict(
        id=5,
        descricao='Família',
        sigla='F',
        quant_sabores=4,
        quant_bordas=2,
        quant_fatias=16
    )
]
