from pyramid.httpexceptions import (
    HTTPOk,
    HTTPNotFound,
    HTTPBadRequest
)
from pyramid.security import remember
from pyramid.view import view_config
from json import dumps
import colander
from .schemas import UserSchema


class UserViews:
    def __init__(self, context, request):
        self.current_user = request.user
        self.context = context
        self.request = request

    @view_config(route_name='users_profile', permission='super',
                 renderer='json', request_method='GET')
    def profile_get(self):
        user = self.current_user
        if user:
            res = dumps(dict(
                data=dict(
                    code=200,
                    email=user.email,
                    username=user.username,
                    firstName=user.first_name,
                    lastName=user.last_name)),
                ensure_ascii=False)
            return HTTPOk(body=res, content_type='application/json; charset=UTF-8')

        msg = 'Usuário não encontrado'
        res = dumps(dict(error=dict(code=404, message=msg)), ensure_ascii=False)
        return HTTPNotFound(body=res, content_type='application/json; charset=UTF-8')

    @view_config(route_name='users_profile', permission='super',
                 renderer='json', request_method='PUT')
    def profile_update(self):
        json_body = self.request.json_body

        # montagem de cstruct elimina necessiade de validação da estrutura do json
        # objetos faltantes retornam colander.null
        cstruct = UserSchema().serialize(json_body)

        # os tipos e dados do json precisam ser validados
        # bind disponibiliza atributos dentro do contexto do schema para validações deferred
        user_schema = UserSchema().bind(current_user=self.current_user,
                                        username=cstruct['username'],
                                        email=cstruct['email'])
        try:
            appstruct = user_schema.deserialize(cstruct)
        except colander.Invalid as er:
            errors = er.asdict()

            error_list = []
            for k, v in errors.items():
                error_list.append({'field': k, 'message': v})

            msg = 'Dados inválidos'
            res = dumps(dict(
                error=dict(
                    code=400,
                    message=msg,
                    errors=error_list)),
                ensure_ascii=False)
            return HTTPBadRequest(body=res, content_type='application/json; charset=UTF-8')

        # formulario valido
        self.context.email = appstruct['email']
        self.context.first_name = appstruct['firstName']
        self.context.last_name = appstruct['lastName']

        msg = 'Sucesso'
        res = dumps(dict(
            data=dict(
                code=200,
                message=msg)),
            ensure_ascii=False)

        # alterações de username necessitam que um novo cookie seja respondido
        if appstruct['username'] != self.context.username:
            self.context.username = appstruct['username']
            headers = remember(self.request, self.context.username)
            return HTTPOk(headers=headers, body=res, content_type='application/json; charset=UTF-8')

        return HTTPOk(body=res, content_type='application/json; charset=UTF-8')
