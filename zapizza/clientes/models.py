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
from ..site.hashid import get_decoded_id


class Cliente(BaseObject):
    __tablename__ = 'clientes'
    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=False)
    hash_id = Column(String(120), index=True, unique=True)
    nome = Column(String(100))
    ativo = Column(Boolean, nullable=False, default=True)

    empresa = relationship('Empresa', back_populates='clientes')

    telefones = relationship("Telefone", back_populates='cliente', cascade="all, delete-orphan")
    enderecos = relationship("Endereco", back_populates='cliente', cascade="all, delete-orphan")


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
    def list(cls, empresa_id):
        """
        :param empresa_id: identificação da empresa do usuário
        :return: lista de objetos encontrados
        """
        return Session.query(cls).filter(cls.empresa_id == empresa_id).order_by(cls.nome).all()

    @classmethod
    def total(cls, empresa_id):
        """
        :param empresa_id: identificação da empresa do usuário
        :return: contagem do total de objetos encontrados
        """
        return Session.query(func.count(cls.id)).filter(cls.empresa_id == empresa_id).first()


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
