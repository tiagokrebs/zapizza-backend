"""
Comum a todas as views
Efetua envio de email avulso síncrono ou assíncrono

todo: email.py deve pertencer ao package site
todo: alterar para pyramid_email
"""

import smtplib
import premailer
from email.message import EmailMessage
from threading import Thread
from pyramid.renderers import render


def send_async_templated_mail(request, recipients, template, context, sender=None):
    """Envia emails de forma assíncrona"""
    thr = Thread(target=send_templated_mail, args=[request, recipients, template, context, sender])
    thr.start()


def send_templated_mail(request, recipients, template, context, sender=None):
    """Envia emails HTML a partir de templates e texto.
    O email é rederizado a partir de três arquivos de template:
    * Lê o assunto de um template especifico para o assunto $template.subject.txt
    * Gera o email em HTML a partir de um template, $template.body.jinja2
    * Gera o email em TXT a partir de um template, $template.body.txt
    """

    assert recipients
    assert len(recipients) > 0

    subject = render(template + ".subject.txt", context, request=request)
    subject = subject.decode('utf-8')

    html_body = render(template + ".body.jinja2", context, request=request)
    text_body = render(template + ".body.txt", context, request=request)
    text_body = text_body.decode('utf-8')

    if not sender:
        sender = request.registry.settings["mail.default_sender"]

    host = request.registry.settings["mail.host"]
    port = request.registry.settings["mail.port"]
    user = request.registry.settings["mail.username"]
    password = request.registry.settings["mail.password"]

    # Inline CSS styles
    html_body = premailer.transform(html_body)
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipients
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype='html')


    # todo: implementar tratamento de exceções
    server = smtplib.SMTP(host=host, port=port)
    server.set_debuglevel(1)
    server.ehlo()
    server.starttls()  # todo: verificar padrão de email zapizza
    server.login(user=user, password=password)
    server.send_message(msg)
    server.close()
