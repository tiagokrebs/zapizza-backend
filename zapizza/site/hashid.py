"""
Método para codificação e decodificação de códigos inteiros para hashids
Inserido de coluna única nas tabelas do banco de dados para uso de sequencial
obfuscado na url do site

Utilizado para codificar chaves primárias de mais de uma tabela
sempre na ordem de herança

Ex: Empresa id 1 -> tamanhos id 123
    hasid = hashids.encode(1, 123)
    url = zapizza.com.br/tamanho/L3Vab2AqRr/edit

    ints = hashids.decode('L3Vab2AqRr')
    (1, 123)

Tupla de retorno sempre inicia com empresas.id seguido dos filhos
Ex: (empresas.id, cliente.id, pedido.id)
"""

from hashids import Hashids
from pyramid.httpexceptions import HTTPForbidden


def generate_hash(salt, listt):
    """
    Gerador da hashid
    :param salt: palavra chave usada na codificação/decodificação da chave
    :param listt: lista contendo os dados a serem codificados
    :return: hashid com no mínimo 6 caracteres
    """
    salt = 'zap ' + salt
    hashid = Hashids(salt=salt, min_length=6)
    return hashid.encode(*listt)


def decode_hash(salt, hashh):
    """
    Decoficador de hashid
    :param salt: palavra chave usada para codificação/decodificação da chave
    :param hashh: hashid
    :return: lista com dados decodificados
    """
    salt = 'zap ' + salt
    hashid = Hashids(salt=salt, min_length=6)
    return hashid.decode(hashh)


def get_decoded_id(salt, hashh, empresa_id):
    """
    Método de retorno de ids codificadas em hashid combinadas com empresa_id
    :param salt: palavra chave para codificação/decodificação da chave
    :param hashh: hashid
    :param empresa_id: código da empresa proprietária da chave
    :return: id decodificado
    """
    data_decoded = decode_hash(salt, hashh)
    if not data_decoded:
        raise HTTPForbidden()
    empresa_id_decoded = data_decoded[0]
    id_decoded = data_decoded[1]
    if empresa_id_decoded != empresa_id:
        raise HTTPForbidden()
    return id_decoded
