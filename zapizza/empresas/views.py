from pyramid.httpexceptions import HTTPFound
from pyramid.view import (
    view_config,
    view_defaults
)
import colander
from deform import Form, ValidationFailure
from pyramid_sqlalchemy import Session
from ..users.models import User
from ..pizzas.models import Tamanho
from pyramid.security import remember
from ..site.hashid import generate_hash