"""
Comum a todos os modelos
Quando em uso de base de dados SQLite método para interpretação de array é necessário
"""

from sqlalchemy.types import (
    String,
    TypeDecorator,
)
import json


class ArrayType(TypeDecorator):
    """ Sqlite não suporte array.
        É utilizado um decorador de tipo customizado.
        Ver http://docs.sqlalchemy.org/en/latest/core/types.html#sqlalchemy.types.TypeDecorator
    """
    impl = String

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        return json.loads(value)

    def copy(self):
        return ArrayType(self.impl.length)
