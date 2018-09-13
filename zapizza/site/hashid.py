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


def generate_hash(salt, listt):
    salt = 'zap ' + salt
    hashid = Hashids(salt=salt, min_length=6)
    return hashid.encode(*listt)


def decode_hash(salt, hashh):
    salt = 'zap ' + salt
    hashid = Hashids(salt=salt, min_length=6)
    return hashid.decode(hashh)
