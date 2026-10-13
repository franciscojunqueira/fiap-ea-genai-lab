# -*- coding: utf-8 -*-
"""Simulador do mainframe de cobrança, entregue pelo fornecedor do core para homologação.

Não faz parte do SGC. Lê uma remessa e escreve o retorno correspondente, com resultados
determinísticos (o mesmo nosso número dá sempre a mesma ocorrência).

Uso: python ferramentas/simula_core.py <remessa> <diretorio_retorno>
"""
import datetime
import os
import sys
from decimal import ROUND_HALF_UP, Decimal

# O core calcula encargos com juros de 1% ao mês pro rata die e multa de 2%
MULTA = Decimal("0.02")
JUROS_DIA = Decimal("0.01") / Decimal("30")


def _linha(nosso_numero, ocorrencia, data, valor):
    centavos = int((valor * 100).quantize(Decimal("1"), ROUND_HALF_UP))
    return ("1" + nosso_numero + ocorrencia + data.strftime("%Y%m%d") + str(centavos).rjust(13, "0")).ljust(200)


def _devido(valor, dias):
    if dias <= 0:
        return valor
    return (valor * (1 + MULTA + JUROS_DIA * dias)).quantize(Decimal("0.01"), ROUND_HALF_UP)


def simular(remessa, dir_retorno):
    saida = []
    with open(remessa, encoding="latin-1") as f:
        for linha in f:
            if not linha.startswith("1"):
                continue
            nn = linha[1:13]
            venc = datetime.datetime.strptime(linha[59:67], "%Y%m%d").date()
            valor = Decimal(int(linha[67:80])) / 100
            emissao = datetime.datetime.strptime(linha[80:88], "%Y%m%d").date()
            caso = int(nn[2:11]) % 10
            if caso == 0:
                saida.append(_linha(nn, "03", emissao, Decimal(0)))  # documento do sacado invalido
                continue
            saida.append(_linha(nn, "02", emissao, Decimal(0)))
            if caso in (1, 2, 3, 4):
                saida.append(_linha(nn, "06", venc - datetime.timedelta(days=2), valor))
            elif caso == 5:
                saida.append(_linha(nn, "06", venc + datetime.timedelta(days=2), valor))
            elif caso == 6:
                saida.append(_linha(nn, "06", venc + datetime.timedelta(days=10), _devido(valor, 10)))
            elif caso == 7:
                saida.append(_linha(nn, "06", venc + datetime.timedelta(days=10), valor))
            elif caso == 9:
                saida.append(_linha(nn, "09", venc + datetime.timedelta(days=60), Decimal(0)))
                saida.append(_linha(nn, "17", venc + datetime.timedelta(days=75), _devido(valor, 75)))
            # caso 8: sacado nao paga
    data = datetime.date.today()
    nome = "RET_%s_%s.txt" % (data.strftime("%Y%m%d"), os.path.basename(remessa)[4:-4])
    os.makedirs(dir_retorno, exist_ok=True)
    caminho = os.path.join(dir_retorno, nome)
    header = ("0" + data.strftime("%Y%m%d")).ljust(200)
    trailer = ("9" + str(len(saida)).rjust(6, "0")).ljust(200)
    with open(caminho, "w", encoding="latin-1", newline="") as f:
        f.write("\r\n".join([header] + saida + [trailer]) + "\r\n")
    print("retorno gerado: %s (%d ocorrencias)" % (caminho, len(saida)))
    return caminho


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    simular(sys.argv[1], sys.argv[2])
