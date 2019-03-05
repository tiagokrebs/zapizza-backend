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
    Numeric
)
from sqlalchemy.orm import relationship
from pyramid_sqlalchemy import BaseObject, Session
from ...site.hashid import get_decoded_id


class Telefone(BaseObject):
    __tablename__ = 'clientes_telefones'
    id = Column(Integer, primary_key=True)
    hash_id = Column(String(120), index=True, unique=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    telefone = Column(String(15))

    cliente = relationship('Cliente', back_populates='telefones')

    def __repr__(self):
        return 'Telefone(%s)' % repr(self.telefone)

    __acl__ = [
        (Allow, 'group:admins', 'super'),
        (Allow, 'group:editors', 'edit'),
        (Allow, 'group:users', 'view'),
    ]

    @classmethod
    def by_hash_id(cls, empresa_id, telefone_hash_id):
        """
        :param empresa_id: identificação da empresa do usuário
        :param telefone_hash_id: identificacao codificada do objeto
        :return: dados do objeto referente ao id decodificado
        """
        decoded_id = get_decoded_id('telefones', telefone_hash_id, empresa_id)
        return Session.query(cls).filter(cls.id == decoded_id).first()

    @classmethod
    def list(cls, cliente_id):
        """
        :param cliente_id: identificação do cliente
        :return: lista de objetos encontrados
        """
        return Session.query(cls).filter(cls.cliente_id == cliente_id).order_by(cls.id).all()

    @classmethod
    def by_telefone(cls, cliente_id, telefone):
        """
        :param cliente_id: identificação do cliente
        :param telefone: telefone do cliente
        :return: objteto encontrado
        """
        return Session.query(cls).filter(and_(cls.cliente_id == cliente_id, cls.telefone == telefone)).first()


def telefone_factory(request):
    """
    Factory é chamada pela view da rota acessada,
    obtem cliHashid de objeto Cliente (pai) e verifica propriedade
    do objeto através de get_decoded_id().
    Busca por objeto Telefone com base em parametro {telHashid} da url.

    :param request: objeto de request do framework
    :return: Endereco, HttpForbiden ou HttpNotFound
    """

    cliente_hash_id = request.matchdict.get('cliHashid')
    get_decoded_id('clientes', cliente_hash_id, request.user.empresa_id)

    telefone_hash_id = request.matchdict.get('telHashid')
    if telefone_hash_id is None:
        return Telefone
    telefone = Telefone.by_hash_id(request.user.empresa_id, telefone_hash_id)
    if not telefone:
        raise HTTPNotFound()
    return telefone
