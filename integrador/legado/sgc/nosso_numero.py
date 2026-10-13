# -*- coding: utf-8 -*-
# nosso numero = carteira (2) + sequencial (9) + DV modulo 11
from sgc import banco, config


def dv_modulo11(numero):
    pesos = [2, 3, 4, 5, 6, 7, 8, 9]
    soma = 0
    for i, digito in enumerate(reversed(numero)):
        soma += int(digito) * pesos[i % len(pesos)]
    resto = soma % 11
    if resto in (0, 1):
        return "0"
    return str(11 - resto)


def gerar(con):
    seq = banco.proximo_valor(con, "nosso_numero_" + config.CEDENTE_CARTEIRA)
    base = config.CEDENTE_CARTEIRA + str(seq).rjust(9, "0")
    return base + dv_modulo11(base)
