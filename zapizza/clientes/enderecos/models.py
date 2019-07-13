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


class Endereco(BaseObject):
    __tablename__ = 'clientes_enderecos'
    id = Column(Integer, primary_key=True)
    hash_id = Column(String(120), index=True, unique=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    cep = Column(String(8), nullable=False)
    logradouro = Column(String(100), nullable=False)
    numero = Column(String(10))
    complemento = Column(String(100))
    bairro = Column(String(100), nullable=False)
    cidade = Column(String(100), nullable=False)
    estado = Column(String(2), nullable=False)

    # one to many
    pedidos = relationship('Pedido', back_populates='endereco', cascade='all, delete')

    def __repr__(self):
        return 'Endereço(%s)' % repr(self.logradouro)

    __acl__ = [
        (Allow, 'group:admins', 'super'),
        (Allow, 'group:editors', 'edit'),
        (Allow, 'group:users', 'view'),
    ]

    @classmethod
    def by_hash_id(cls, empresa_id, endereco_hash_id):
        """
        :param empresa_id: identificação da empresa do usuário
        :param endereco_hash_id: identificacao codificada do objeto
        :return: dados do objeto referente ao id decodificado
        """
        decoded_id = get_decoded_id('enderecos', endereco_hash_id, empresa_id)
        return Session.query(cls).filter(cls.id == decoded_id).first()

    @classmethod
    def list(cls, cliente_id):
        """
        :param cliente_id: identificação do cliente
        :return: lista de objetos encontrados
        """
        return Session.query(cls).filter(cls.cliente_id == cliente_id).order_by(cls.logradouro).all()

    @classmethod
    def by_logradouro(cls, cliente_id, logradouro):
        """
        :param cliente_id: identificação do cliente
        :param logradouro: logradouro do cliente
        :return: objteto encontrado
        """
        return Session.query(cls).filter(and_(cls.cliente_id == cliente_id, cls.logradouro == logradouro)).first()


def endereco_factory(request):
    """
    Factory é chamada pela view da rota acessada,
    obtem cliHashid de objeto Cliente (pai) e verifica propriedade
    do objeto através de get_decoded_id().
    Busca por objeto Endereco com base em parametro {endHashid} da url.

    :param request: objeto de request do framework
    :return: Endereco, HttpForbiden ou HttpNotFound
    """

    cliente_hash_id = request.matchdict.get('cliHashid')
    get_decoded_id('clientes', cliente_hash_id, request.user.empresa_id)

    endereco_hash_id = request.matchdict.get('endHashid')
    if endereco_hash_id is None:
        return Endereco
    endereco = Endereco.by_hash_id(request.user.empresa_id, endereco_hash_id)
    if not endereco:
        raise HTTPNotFound()
    return endereco
