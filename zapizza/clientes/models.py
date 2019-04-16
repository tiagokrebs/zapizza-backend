from pyramid.httpexceptions import HTTPNotFound
from pyramid.security import Allow

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
    func,
    and_,
    Numeric,
    asc,
    desc
)
from sqlalchemy.orm import relationship, joinedload, load_only
from pyramid_sqlalchemy import BaseObject, Session
from ..site.hashid import get_decoded_id
from .telefones.models import Telefone


class Cliente(BaseObject):
    __tablename__ = 'clientes'
    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=False)
    hash_id = Column(String(120), index=True, unique=True)
    nome = Column(String(100))
    ativo = Column(Boolean, nullable=False, default=True)

    # many to one
    empresa = relationship('Empresa', back_populates='clientes')

    # one to many
    telefones = relationship("Telefone", cascade="all, delete-orphan")
    enderecos = relationship("Endereco", cascade="all, delete-orphan")

    def __repr__(self):
        return 'Cliente(%s)' % repr(self.nome)

    __acl__ = [
        (Allow, 'group:admins', 'super'),
        (Allow, 'group:editors', 'edit'),
        (Allow, 'group:users', 'view'),
    ]

    @classmethod
    def by_hash_id(cls, empresa_id, cliente_hash_id):
        """
        :param empresa_id: identificação da empresa do usuário
        :param cliente_hash_id: identificacao codificada do objeto
        :return: dados do objeto referente ao id decodificado
        """
        decoded_id = get_decoded_id('clientes', cliente_hash_id, empresa_id)
        return Session.query(cls).filter(cls.id == decoded_id).first()

    @classmethod
    def list(cls, empresa_id, offset, limit, sort, order, nome, ativo):
        """
        Método para retorno com paginação e ordenação remotas
        :param empresa_id: identificação da empresa
        :param offset: ponteiro inicial da consulta
        :param limit: limite de registros
        :param sort: coluna de ordenação
        :param order: tipo de ordenação
        :param nome: filtro para a coluna nome
        :param ativo: filtro para a coluna ativo
        :return:
        """

        s = asc('clientes_' + sort)  # joinedload obriga concatenação
        if order == 'desc':
            s = desc(sort)

        # todo: parametro 'q' para lista completa ou lista para select (novo ClienteSelectSchema)
        # todo: é necessário um método para filtros dinâmicos de acordo com modelo

        if nome and ativo:
            return Session.query(cls)\
                .filter(and_(cls.empresa_id == empresa_id, cls.nome.ilike('%' + nome + '%'), cls.ativo == ativo))\
                .options(joinedload(cls.telefones), joinedload(cls.enderecos))\
                .order_by(s).limit(limit).offset(offset).all()
        elif nome:
            return Session.query(cls) \
                .filter(and_(cls.empresa_id == empresa_id, cls.nome.ilike('%' + nome + '%'))) \
                .options(joinedload(cls.telefones), joinedload(cls.enderecos)) \
                .order_by(s).limit(limit).offset(offset).all()
        elif ativo:
            return Session.query(cls) \
                .filter(and_(cls.empresa_id == empresa_id, cls.ativo == ativo)) \
                .options(joinedload(cls.telefones), joinedload(cls.enderecos)) \
                .order_by(s).limit(limit).offset(offset).all()
        else:
            return Session.query(cls).filter(cls.empresa_id == empresa_id).order_by(s) \
                .options(joinedload(cls.telefones), joinedload(cls.enderecos)) \
                .limit(limit).offset(offset).all()

    @classmethod
    def total(cls, empresa_id, nome, ativo):

        # todo: é necessário um método para filtros dinâmicos de acordo com modelo

        if nome and ativo:
            return Session.query(func.count(cls.id)) \
                .filter(and_(cls.empresa_id == empresa_id, cls.nome.ilike('%' + nome + '%'), cls.ativo == ativo))\
                .first()
        elif nome:
            return Session.query(func.count(cls.id)) \
                .filter(and_(cls.empresa_id == empresa_id, cls.nome.ilike('%' + nome + '%'))) \
                .first()
        elif ativo:
            return Session.query(func.count(cls.id)) \
                .filter(and_(cls.empresa_id == empresa_id, cls.ativo == ativo)) \
                .first()
        else:
            return Session.query(func.count(cls.id))\
                .filter(cls.empresa_id == empresa_id)\
                .first()

    @classmethod
    def select_list(cls, empresa_id, limit, nome, telefone):
        """
        Método de seleção de dados para componentes tipo select
        :param empresa_id: identificacao da empresa
        :param limit: limite de registros
        :param nome: filtro para atributo nome
        :param telefone: filtro para atributo telefone
        :return:
        """
        if nome:
            return Session.query(cls.hash_id, cls.nome) \
                .filter(and_(cls.empresa_id == empresa_id, cls.nome.ilike('%' + nome + '%'), cls.ativo == True)) \
                .order_by(cls.nome).limit(limit).all()
        elif telefone:
            return Session.query(cls.hash_id, Telefone.telefone) \
                .join(cls.telefones) \
                .filter(and_(cls.empresa_id == empresa_id, cls.ativo == True)) \
                .filter(Telefone.telefone.like('%' + telefone + '%')) \
                .order_by(Telefone.telefone).limit(limit).all()

def cliente_factory(request):
    """
    Factory é chamada pela view da rota acessada,
    busca por objeto Cliente com base em parametro {hashid} da url.

    :param request: objeto de request do framework
    :return: Cliente ou HttpNotFound caso busca retorne nulo
    """
    cliente_hash_id = request.matchdict.get('hashid')
    if cliente_hash_id is None:
        return Cliente
    cliente = Cliente.by_hash_id(request.user.empresa_id, cliente_hash_id)
    if not cliente:
        raise HTTPNotFound()
    return cliente
