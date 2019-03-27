import os
import sys
import transaction
import datetime

from pyramid.config import Configurator
from pyramid_sqlalchemy import Session
from pyramid_sqlalchemy.meta import metadata
from pyramid.paster import get_appsettings, setup_logging
from sqlalchemy import Sequence

from ..site.hashid import generate_hash
from ..empresas.models import Empresa, sample_empresas
from ..users.models import User, sample_users
# from ..pizzas.models import (
#     Tamanho,
#     sample_tamanhos,
#     Sabor,
#     sample_sabores,
#     SaborTamanho
# )

# todo: separar script para inicialização do bd (apenas com usuários) e inicialização dos dados (pizza...)

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

        # # adiciona empresas
        # for empresa in sample_empresas:
        #     e = Empresa(id=empresa['id'],
        #                 razao_social=empresa['razao_social'])
        #     lista_chaves = [empresa['id']]
        #     e.hash_id = generate_hash('empresas', lista_chaves)
        #     Session.add(e)
        #     seq = Sequence('empresas_id_seq')
        #     Session.execute(seq)
        #
        # # obtem empresa pai para adicionar os filhos
        # empresa = Empresa.by_razao(sample_empresas[0]['razao_social'])
        #
        # # adiciona users
        # for user in sample_users:
        #     u = User(
        #         id=user['id'],
        #         email=user['email'],
        #         username=user['username'],
        #         password=user['password'],
        #         first_name=user['first_name'],
        #         last_name=user['last_name'],
        #         groups=user['groups'],
        #         register_date=datetime.datetime.now(),
        #         register_confirm=datetime.datetime.now()
        #     )
        #     lista_chaves = [empresa.id, user['id']]
        #     u.hash_id = generate_hash('users', lista_chaves)
        #     u.empresa = empresa
        #     Session.add(u)
        #     seq = Sequence('users_id_seq')
        #     Session.execute(seq)
        #
        # # adiciona tamanhos
        # for tamanho in sample_tamanhos:
        #     t = Tamanho(
        #         id=tamanho['id'],
        #         descricao=tamanho['descricao'],
        #         sigla=tamanho['sigla'],
        #         quant_sabores=tamanho['quant_sabores'],
        #         quant_bordas=tamanho['quant_bordas'],
        #         quant_fatias=tamanho['quant_fatias'],
        #         ativo=tamanho['ativo']
        #     )
        #     lista_chaves = [empresa.id, tamanho['id']]
        #     t.hash_id = generate_hash('tamanhos', lista_chaves)
        #     t.empresa = empresa
        #     Session.add(t)
        #     Session.flush()
        #     seq = Sequence('tamanhos_id_seq')
        #     Session.execute(seq)
        #
        # # adiciona sabores
        # for sabor in sample_sabores:
        #     s = Sabor(
        #         id=sabor['id'],
        #         descricao=sabor['descricao'],
        #         ativo=sabor['ativo']
        #     )
        #     lista_chaves = [empresa.id, sabor['id']]
        #     s.hash_id = generate_hash('sabores', lista_chaves)
        #     s.empresa = empresa
        #     Session.add(s)
        #     Session.flush()
        #     seq = Sequence('sabores_id_seq')
        #     Session.execute(seq)
        #
        #     # adiciona tamanhos dos sabores
        #     for tamanho in sample_tamanhos:
        #         if tamanho['sigla'] == 'B':
        #             valor = 20
        #         elif tamanho['sigla'] == 'P':
        #             valor = 25
        #         elif tamanho['sigla'] == 'M':
        #             valor = 30
        #         elif tamanho['sigla'] == 'G':
        #             valor = 35
        #         elif tamanho['sigla'] == 'F':
        #             valor = 40
        #         st = SaborTamanho(
        #             sabor_id=sabor['id'],
        #             tamanho_id=tamanho['id'],
        #             valor=valor
        #         )
        #         Session.add(st)

