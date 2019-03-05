from pyramid.httpexceptions import HTTPNotFound
from pyramid.security import Allow

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
    func,
    desc,
    asc,
    and_
)
from sqlalchemy.orm import relationship
from pyramid_sqlalchemy import BaseObject, Session
from ...site.hashid import get_decoded_id


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
    ativo = Column(Boolean, nullable=False, default=True)

    empresa = relationship('Empresa', back_populates='tamanhos')

    def __repr__(self):
        return 'Tamanho(%s)' % repr(self.descricao)

    # coluna para permissão por registro
    # default_acl = [
    #    (Allow, Everyone, 'view'),
    #    (Allow, 'group:editors', 'edit')
    # ]

    # permissões
    __acl__ = [
        (Allow, 'group:admins', 'super'),
        (Allow, 'group:editors', 'edit'),
        (Allow, 'group:users', 'view'),
    ]

    # método para retorno de __acl__ por registro
    # def __acl__(self=None):
    #    return getattr(self, 'acl', None) or ToDo.default_acl

    # decodifica hash_id recebido, certifica empresa_id e retorna Tamanho filtrado
    @classmethod
    def by_hash_id(cls, empresa_id, tamanho_hash_id):
        decoded_id = get_decoded_id('tamanhos', tamanho_hash_id, empresa_id)
        return Session.query(cls).filter(cls.id == decoded_id).first()

    # retorna lista de Tamanho filtrado por empresa
    @classmethod
    def list(cls, empresa_id, offset, limit, sort, order):
        s = asc(sort)
        if order == 'desc':
            s = desc(sort)
        return Session.query(cls).filter(cls.empresa_id == empresa_id).order_by(s)\
            .limit(limit).offset(offset).all()

    @classmethod
    def total(cls, empresa_id):
        return Session.query(func.count(cls.id)).filter(cls.empresa_id == empresa_id).first()

    @classmethod
    def by_descricao(cls, empresa_id, descricao):
        return Session.query(cls).filter(and_(cls.empresa_id == empresa_id, cls.descricao == descricao)).first()


""" 
A factory do obtem hashid da url da rota. Exemplo /tamanhos/{hashid}/edit
Quando não existe o parâmetro {hasihd} uma instância vazia do objeto é retornada
Quando o parâmetro {hashid} existe e o objeto existe a instância de objeto desse hashid é retornada
Quando o parâmetro {hashid} existe e o objeto não existe retorna página não encontrada

Também é obtido o usuário autenticado do request para a descoberta da empresa
Quando os dados de objeto são filtrados é passada a hashid contendo a tupla (empresa_id, objeto_id)
juntamente com o empresa_id do usuário logado
Caso o método de pesquisa de objeto falhe por diferença entre empresa_id forbidden é retornado
"""


def tamanho_factory(request):
    tamanho_hash_id = request.matchdict.get('hashid')
    if tamanho_hash_id is None:
        return Tamanho
    tamanho = Tamanho.by_hash_id(request.user.empresa_id, tamanho_hash_id)
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
        quant_fatias=4,
        ativo=False
    ),
    dict(
        id=2,
        descricao='Pequena',
        sigla='P',
        quant_sabores=2,
        quant_bordas=1,
        quant_fatias=6,
        ativo=False
    ),
    dict(
        id=3,
        descricao='Média',
        sigla='M',
        quant_sabores=3,
        quant_bordas=1,
        quant_fatias=9,
        ativo=True
    ),
    dict(
        id=4,
        descricao='Grande',
        sigla='G',
        quant_sabores=4,
        quant_bordas=2,
        quant_fatias=12,
        ativo=True
    ),
    dict(
        id=5,
        descricao='Família',
        sigla='F',
        quant_sabores=4,
        quant_bordas=2,
        quant_fatias=16,
        ativo=True
    )
]
