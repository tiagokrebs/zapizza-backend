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
    DateTime,
    JSON,
    Text,
    asc,
    desc,

)
from sqlalchemy.orm import relationship, joinedload
from pyramid_sqlalchemy import BaseObject, Session
from sqlalchemy.sql.functions import now
from ..site.hashid import get_decoded_id


class Pedido(BaseObject):
    __tablename__ = 'pedidos'
    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=False)
    hash_id = Column(String(50), index=True, unique=True)
    finalizacao = Column(DateTime, nullable=False, default=now())
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    pedido_json = Column(JSON, nullable=False)
    tipo_entrega = Column(String(1), nullable=False)
    endereco_id = Column(Integer, ForeignKey('clientes_enderecos.id'), nullable=False)
    obs_entrega = Column(Text)
    valor_total = Column(Numeric(precision=6, scale=2), nullable=False)

    # many to one
    empresa = relationship('Empresa', back_populates='pedidos')
    cliente = relationship('Cliente', back_populates='pedidos')
    endereco = relationship('Endereco', back_populates='pedidos')

    def __repr__(self):
        return 'Pedido(%s)' % repr(self.hash_id)

    __acl__ = [
        (Allow, 'group:admins', 'super'),
        (Allow, 'group:editors', 'edit'),
        (Allow, 'group:users', 'view'),
    ]

    @classmethod
    def by_hash_id(cls, empresa_id, pedido_hash_id):
        """
        :param empresa_id: identificação da empresa do usuário
        :param pedido_hash_id: identificacao codificada do objeto
        :return: dados do objeto referente ao id decodificado
        """
        decoded_id = get_decoded_id('pedidos', pedido_hash_id, empresa_id)
        return Session.query(cls).filter(cls.id == decoded_id).first()

    @classmethod
    def list(cls, empresa_id, offset, limit, sort, order, cliente):
        """
        Método para retorno com paginação e ordenação remotas
        :param empresa_id: identificação da empresa
        :param offset: ponteiro inicial da consulta
        :param limit: limite de registros
        :param sort: coluna de ordenação
        :param order: tipo de ordenação
        :param cliente: filtro para a coluna cliente_id (hash_id)
        :return:
        """

        s = asc('pedidos_' + sort)  # joinedload obriga concatenação
        if order == 'desc':
            s = desc(sort)

        # todo: parametro 'q' para lista completa ou lista para select (novo ClienteSelectSchema)
        # todo: é necessário um método para filtros dinâmicos de acordo com modelo

        if cliente:
            decoded_id = get_decoded_id('clientes', cliente, empresa_id)
            return Session.query(cls) \
                .filter(and_(cls.empresa_id == empresa_id, cls.cliente_id == decoded_id)) \
                .order_by(s).limit(limit).offset(offset).all()
        else:
            return Session.query(cls).filter(cls.empresa_id == empresa_id).order_by(s) \
                .limit(limit).offset(offset).all()

    @classmethod
    def total(cls, empresa_id, cliente):

        # todo: é necessário um método para filtros dinâmicos de acordo com modelo

        if cliente:
            decoded_id = get_decoded_id('clientes', cliente, empresa_id)
            return Session.query(func.count(cls.id)) \
                .filter(and_(cls.empresa_id == empresa_id, cls.cliente_id == decoded_id)) \
                .first()
        else:
            return Session.query(func.count(cls.id)) \
                .filter(cls.empresa_id == empresa_id) \
                .first()

#     todo: método para obter filtrado por cliente


def pedido_factory(request):
    """
    Factory é chamada pela view da rota acessada,
    busca por objeto Pedido com base em parametro {hashid} da url.

    :param request: objeto de request do framework
    :return: Pedido ou HttpNotFound caso busca retorne nulo
    """
    pedido_hash_id = request.matchdict.get('hashid')
    if pedido_hash_id is None:
        return Pedido
    pedido = Pedido.by_hash_id(request.user.empresa_id, pedido_hash_id)
    if not pedido:
        raise HTTPNotFound()
    return pedido
