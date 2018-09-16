# todo: método para retirar rotas do init principal
# O bloco abaixo pode ser utilizado para retirar as rotas e views
# do arquivo __init__.py do pacote principal

#from pyramid.config import Configurator

#def main(global_config, **settings):
#    config = Configurator(settings=settings)
#    config.scan()
#    config.include(add_routes(config))

#def add_routes(config):
#    # rotas Tamanho com route factory
#    config.add_route('tamanhos_list', '/tamanhos',
#                     factory='.tamanhos.models.tamanho_factory')
#    config.add_route('tamanhos_add', '/tamanhos/add',
#                     factory='.tamanhos.models.tamanho_factory')
#    config.add_route('tamanhos_view', '/tamanhos/{id}',
#                     factory='.tamanhos.models.tamanho_factory')
#    config.add_route('tamanhos_edit', '/tamanhos/{id}/edit',
#                     factory='.tamanhos.models.tamanho_factory')
#    config.add_route('tamanhos_delete', '/tamanhos/{id}/delete',
#                     factory='.tamanhos.models.tamanho_factory')
