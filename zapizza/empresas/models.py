from sqlalchemy import (
    Column,
    Integer,
    String
)
from sqlalchemy.orm import relationship
from pyramid_sqlalchemy import BaseObject


# Modelo da empresa
class Empresa(BaseObject):
    __tablename__ = 'empresas'
    id = Column(Integer, primary_key=True)
    hash_id = Column(String(50), index=True, unique=True)
    razao_social = Column(String(100))

    # todo: back_populates é mesmo nencessário? Interfere no desempenho das consultas?
    users = relationship('User', back_populates='empresa', cascade='all, delete')
    tamanhos = relationship('Tamanho', back_populates='empresa', cascade='all, delete')
    sabores = relationship('Sabor', back_populates='empresa', cascade='all, delete')
    bordas = relationship('Borda', back_populates='empresa', cascade='all, delete')
    bebidas = relationship('Bebida', back_populates='empresa', cascade='all, delete')
    clientes = relationship('Cliente', back_populates='empresa', cascade='all, delete')


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
