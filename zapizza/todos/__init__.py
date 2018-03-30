# O bloco abaixo pode ser utilizado para retirar as rotas e views
# do arquivo __init__.py do pacote principal
#
#from pyramid.config import Configurator
#
#def main(global_config, **settings):
#    config = Configurator(settings=settings)
#    config.scan()
#    config.include(add_routes(config))
#
#def add_routes(config):
#    # To Do routes with route factory
#    config.add_route('todos_list', '/todos',
#                     factory='.todos.models.todo_factory')
#    config.add_route('todos_add', '/todos/add',
#                     factory='.todos.models.todo_factory')
#    config.add_route('todos_view', '/todos/{id}',
#                     factory='.todos.models.todo_factory')
#    config.add_route('todos_edit', '/todos/{id}/edit',
#                     factory='.todos.models.todo_factory')
#    config.add_route('todos_delete', '/todos/{id}/delete',
#                     factory='.todos.models.todo_factory')
