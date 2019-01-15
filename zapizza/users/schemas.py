from zapizza.users.models import User
import colander


@colander.deferred
def deferred_email_validator(node, kw):
    current_user = kw.get('current_user')
    email = kw.get('email')
    if email is None or email == current_user.email:
        return colander.Email(msg='E-mail inválido')
    else:
        return colander.All(colander.Email(msg='Email inválido'),
                            colander.Function(email_validator))


@colander.deferred
def deferred_username_validator(node, kw):
    current_user = kw.get('current_user')
    username = kw.get('username')
    if username is None or username == current_user.username:
        return colander.All(colander.Regex(regex=r"^[a-zA-Z0-9]+$", msg='Informe apenas letras e números'),
                            colander.Length(min=3, max=120,
                                            min_err='informe no mínimo 3 caracteres',
                                            max_err='Informa no máximo 120 caracteres'))
    else:
        return colander.All(colander.Regex(regex=r"^[a-zA-Z0-9]+$", msg='Informe apenas letras e números'),
                            colander.Length(min=3, max=120,
                                            min_err='informe no mínimo 3 caracteres',
                                            max_err='Informa no máximo 120 caracteres'),
                            colander.Function(username_validator))


def email_validator(email):
    if User.by_email(email):
        return 'Este e-mail já está em uso'
    else:
        True


def username_validator(username):
    if User.by_username(username):
        return 'Este username já está em uso'
    else:
        return True


class UserSchema(colander.MappingSchema):
    email = colander.SchemaNode(colander.String(),
                                name='email', missing=colander.required,
                                missing_msg='Campo obrigatório',
                                validator=deferred_email_validator,
                                title='E-mail', description='E-mail do usuário')
    username = colander.SchemaNode(colander.String(),
                                   name='username', missing=colander.required,
                                   missing_msg='Campo obrigatório',
                                   validator=deferred_username_validator,
                                   title='Username', description='Username do usuário')
    first_name = colander.SchemaNode(colander.String(),
                                     name='firstName', missing=colander.required,
                                     missing_msg='Campo obrigatório',
                                     validator=colander.All(colander.Regex(regex=r"^[a-zA-Z]+$",
                                                                           msg='Informe apenas o primeiro nome'),
                                                            colander.Length(min=3, max=120,
                                                                            min_err='informe no mínimo 3 caracteres',
                                                                            max_err='Informa no máximo 120 caracteres')),
                                     title='Primeiro nome', description='Primeiro nome do usuário')
    last_name = colander.SchemaNode(colander.String(),
                                    name='lastName', missing=colander.required,
                                    missing_msg='Campo obrigatório',
                                    validator=colander.All(colander.Regex(regex=r"^[a-zA-Z]+$",
                                                                          msg='Informe apenas o último nome'),
                                                           colander.Length(min=3, max=120,
                                                                           min_err='informe no mínimo 3 caracteres',
                                                                           max_err='Informa no máximo 120 caracteres')),
                                    title='Último nome', description='Último nome do usuário')
