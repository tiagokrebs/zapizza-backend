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


class Borda(BaseObject):
    __tablename__ = 'bordas'
    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=False)
    hash_id = Column(String(120), index=True, unique=True)
    descricao = Column(String(120), nullable=False)
    valor = Column(Numeric(precision=6, scale=2), nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)

    empresa = relationship('Empresa', back_populates='bordas')

    def __repr__(self):
        return 'Borda(%s)' % repr(self.descricao)

    __acl__ = [
        (Allow, 'group:admins', 'super'),
        (Allow, 'group:editors', 'edit'),
        (Allow, 'group:users', 'view'),
    ]

    @classmethod
    def by_hash_id(cls, empresa_id, borda_hash_id):
        """
        :param empresa_id: identificação da empresa do usuário
        :param borda_hash_id: identificacao codificada do objeto
        :return: dados do objeto referente ao id decodificado
        """
        decoded_id = get_decoded_id('bordas', borda_hash_id, empresa_id)
        return Session.query(cls).filter(cls.id == decoded_id).first()

    @classmethod
    def list(cls, empresa_id):
        """
        :param empresa_id: identificação da empresa do usuário
        :return: lista de objetos encontrados
        """
        return Session.query(cls).filter(cls.empresa_id == empresa_id).order_by(cls.descricao).all()

    @classmethod
    def total(cls, empresa_id):
        """
        :param empresa_id: identificação da empresa do usuário
        :return: contagem do total de objetos encontrados
        """
        return Session.query(func.count(cls.id)).filter(cls.empresa_id == empresa_id).first()

    @classmethod
    def by_descricao(cls, empresa_id, descricao):
        """
        Busca por descrição é utilizada na validação de POST/PUT do objeto

        :param empresa_id: identificação da empresa do usuário
        :param descricao: descrição do objeto
        :return: objeto encontrado
        """
        return Session.query(cls).filter(and_(cls.empresa_id == empresa_id, cls.descricao == descricao)).first()


def borda_factory(request):
    """
    Factory é chamada pela view da rota acessada,
    busca por objeto Borda com base em parametro {hashid} da url.

    :param request: objeto de request do framework
    :return: Borda ou HttpNotFound caso busca retorne nulo
    """
    borda_hash_id = request.matchdict.get('hashid')
    if borda_hash_id is None:
        return Borda
    borda = Borda.by_hash_id(request.user.empresa_id, borda_hash_id)
    if not borda:
        raise HTTPNotFound()
    return borda
