import os
import sys
import transaction

from pyramid.config import Configurator
from pyramid_sqlalchemy import Session
from pyramid_sqlalchemy.meta import metadata
from pyramid.paster import get_appsettings, setup_logging

from ..todos.models import ToDo, sample_todos
from ..users.models import User, sample_users
from ..pizzas.models import Borda, sample_bordas
from ..pizzas.models import Bebida, sample_bebidas


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    # Usage and configuration
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    config = Configurator(settings=settings)
    config.include('pyramid_sqlalchemy')

    # Make the database with schema and default data
    with transaction.manager:
        metadata.create_all()
        for user in sample_users:
            u = User(
                id=user['id'],
                email=user['email'],
                username=user['username'],
                password=user['password'],
                first_name=user['first_name'],
                last_name=user['last_name'],
                groups=user['groups']
            )
            Session.add(u)

        # Get a user to be the owner of content
        owner = User.by_username(sample_users[0]['username'])

        # Now add todos
        for todo in sample_todos:
            t = ToDo(title=todo['title'],
                     acl=todo.get('acl'))
            t.owner = owner
            Session.add(t)

        # Now add bordas
        for borda in sample_bordas:
            b = Borda(nome_borda=borda['nome_borda'],
                      valor_borda=borda['valor_borda'])
            Session.add(b)

        # Now add bebidas
        for bebida in sample_bebidas:
            b = Bebida(nome_bebida=bebida['nome_bebida'],
                      valor_bebida=bebida['valor_bebida'])
            Session.add(b)