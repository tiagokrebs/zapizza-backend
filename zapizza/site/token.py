"""
Método para geração e validação de tokens JWT com PyJWT
Usado inicialmente para criação de URLs dinâmicas de confirmações via email como registro e login
O email é utilizado como identificador de confirmação que o token é válido

jwt_token = jwt.encode({"exp": datetime.utcnow() + timedelta(seconds=10),
                        "aud":"registro",
                        "email":"krebstiago"}, secret, algorithm='HS512')

jwt.decode(jwt_token, secret, audience='registro', algorithms='HS512')


todo: trocar para pyramid_jwt
"""

import jwt


def generate_token(request, data):
    secret = request.registry.settings["token.secret"]
    return jwt.encode(data, secret, algorithm='HS512')


def confirm_token(request, token, audience):
    secret = request.registry.settings["token.secret"]
    try:
        data = jwt.decode(token, secret, audience=audience, algorithms='HS512')
    except:
        return False
    return data
