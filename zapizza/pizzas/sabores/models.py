from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden
from pyramid.security import Allow

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    and_,
    Boolean,
    func,
    Numeric
)
from sqlalchemy.orm import relationship
from pyramid_sqlalchemy import BaseObject, Session
from ...site.hashid import get_decoded_id


class Sabor(BaseObject):
    __tablename__ = 'sabores'
    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=False)
    hash_id = Column(String(120), index=True, unique=True)
    descricao = Column(String(120), nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)

    empresa = relationship('Empresa')
    tamanhos = relationship("SaborTamanho", cascade="all, delete-orphan")

    def __repr__(self):
        return 'Sabor(%s)' % repr(self.descricao)

    # permissões
    __acl__ = [
        (Allow, 'group:admins', 'super'),
        (Allow, 'group:editors', 'edit'),
        (Allow, 'group:users', 'view'),
    ]

    # decodifica hash_id recebido, certifica empresa_id e retorna Sabor filtrado
    @classmethod
    def by_hash_id(cls, empresa_id, sabor_hash_id):
        decoded_id = get_decoded_id('sabores', sabor_hash_id, empresa_id)
        return Session.query(cls).filter(cls.id == decoded_id).first()

    # retorna lista de Tamanho filtrado por empresa
    @classmethod
    def list(cls, empresa_id):
        return Session.query(cls).filter(cls.empresa_id == empresa_id).order_by(cls.descricao).all()

    @classmethod
    def total(cls, empresa_id):
        return Session.query(func.count(cls.id)).filter(cls.empresa_id == empresa_id).first()

    # pesquisa por descrição
    @classmethod
    def by_descricao(cls, empresa_id, descricao):
        return Session.query(cls).filter(and_(cls.empresa_id == empresa_id, cls.descricao == descricao)).first()


class SaborTamanho(BaseObject):
    __tablename__ = 'sabores_tamanhos'
    sabor_id = Column(Integer, ForeignKey('sabores.id'), nullable=False, primary_key=True)
    tamanho_id = Column(Integer, ForeignKey('tamanhos.id'), nullable=False, primary_key=True)
    valor = Column(Numeric(precision=6, scale=2))

    tamanho = relationship("Tamanho")


def sabor_factory(request):
    sabor_hash_id = request.matchdict.get('hashid')
    if sabor_hash_id is None:
        # retorna a classe
        return Sabor
    sabor = Sabor.by_hash_id(request.user.empresa_id, sabor_hash_id)
    if not sabor:
        raise HTTPNotFound()
    return sabor


# dados exemplo
sample_sabores = [
    dict(
        id=1,
        descricao='Napolitana',
        ativo=True
    ),
    dict(
        id=2,
        descricao='Muzzarela',
        ativo=True
    ),
    dict(
        id=3,
        descricao='Calabresa',
        ativo=True
    )
]
