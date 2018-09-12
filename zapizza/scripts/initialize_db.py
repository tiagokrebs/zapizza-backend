import os
import sys
import transaction
import datetime

from pyramid.config import Configurator
from pyramid_sqlalchemy import Session
from pyramid_sqlalchemy.meta import metadata
from pyramid.paster import get_appsettings, setup_logging

from ..site.hashid import generate_hash
from ..empresas.models import Empresa, sample_empresas
from ..users.models import User, sample_users
from ..tamanhos.models import Tamanho, sample_tamanhos


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    # Usagem e configuração
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    config = Configurator(settings=settings)
    config.include('pyramid_sqlalchemy')

    # Cria o banco de dados com o schema e dados de exemplo
    with transaction.manager:
        metadata.create_all()

        # adiciona empresas
        for empresa in sample_empresas:
            e = Empresa(id=empresa['id'],
                        razao_social=empresa['razao_social'])
            lista_chaves = [empresa['id']]
            e.hash_id = generate_hash('empresas', lista_chaves)
            Session.add(e)

        # obtem empresa pai para adicionar os filhos
        empresa = Empresa.by_razao(sample_empresas[0]['razao_social'])

        # adiciona users
        for user in sample_users:
            u = User(
                id=user['id'],
                email=user['email'],
                username=user['username'],
                password=user['password'],
                first_name=user['first_name'],
                last_name=user['last_name'],
                groups=user['groups'],
                register_date=datetime.datetime.now(),
                register_confirm=datetime.datetime.now()
            )
            lista_chaves = [empresa.id, user['id']]
            u.hash_id = generate_hash('users', lista_chaves)
            u.empresa = empresa
            Session.add(u)

        # adiciona tamanhos
        for tamanho in sample_tamanhos:
            t = Tamanho(
                id=tamanho['id'],
                descricao=tamanho['descricao'],
                sigla=tamanho['sigla'],
                quant_sabores=tamanho['quant_sabores'],
                quant_bordas=tamanho['quant_bordas'],
                quant_fatias=tamanho['quant_fatias']
            )
            lista_chaves = [empresa.id, tamanho['id']]
            t.hash_id = generate_hash('tamanhos', lista_chaves)
            t.empresa = empresa
            Session.add(t)
