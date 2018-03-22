from pyramid.httpexceptions import HTTPNotFound
from pyramid.security import Allow, Everyone
from sqlalchemy import (
    Column,
    String,
    Integer,
    Numeric
)
from sqlalchemy.orm import relationship, backref
from pyramid_sqlalchemy import BaseObject, Session

# SQLite doesn't support arrays, workaround
from ..columns import ArrayType


class Borda(BaseObject):
    __tablename__ = 'bordas'
    id = Column(Integer, primary_key=True)
    nome_borda = Column(String(50), nullable=False)
    valor_borda = Column(Numeric(precision=8, scale=2), nullable=False)

    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, 'group:editors', 'edit')
    ]


def borda_factory(request):
    borda_id = request.matchdict.get('id')
    if borda_id is None:
        # Return the class
        return Borda
    borda_id_int = int(borda_id)
    borda = Session.query(Borda).filter_by(id=borda_id_int).first()
    if not borda:
        raise HTTPNotFound()
    return borda


sample_bordas = [
    dict(
        id=1,
        nome_borda='Queijo cheddar',
        valor_borda=3.00
    ),
    dict(
        nome_borda='Doce de Leite',
        valor_borda=3.00
    )
]
