"""
Common to all models.
Quando em uso de base de dados SQLite metodo para interpretacao de array e necessario
"""

from sqlalchemy.types import (
    String,
    TypeDecorator,
)
import json


class ArrayType(TypeDecorator):
    """ Sqlite does not support arrays.
        Let's use a custom type decorator.

        See http://docs.sqlalchemy.org/en/latest/core/types.html#sqlalchemy.types.TypeDecorator
    """
    impl = String

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        return json.loads(value)

    def copy(self):
        return ArrayType(self.impl.length)


