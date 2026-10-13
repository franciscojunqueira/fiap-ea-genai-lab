# -*- coding: utf-8 -*-
# funcoes de apoio usadas por varios modulos
import datetime
import logging
import sys
import unicodedata

from sgc import config

_log = None


def log():
    global _log
    if _log is None:
        _log = logging.getLogger("sgc")
        h = logging.StreamHandler(sys.stdout)
        h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        _log.addHandler(h)
        _log.setLevel(config.LOG_NIVEL)
    return _log


def normaliza_nome(nome):
    # chave de cruzamento com o cadastro de sacados: maiusculas, sem acento, sem espaco duplo
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode("ascii")
    return " ".join(sem_acento.upper().split())


def so_digitos(texto):
    return "".join(c for c in texto if c.isdigit())


def para_data(texto):
    if isinstance(texto, datetime.date):
        return texto
    texto = texto.strip()[:10]
    if "/" in texto:
        return datetime.datetime.strptime(texto, "%d/%m/%Y").date()
    return datetime.datetime.strptime(texto, "%Y-%m-%d").date()


def campo_alfa(valor, tamanho):
    # campos alfanumericos do layout: sem acento, maiusculo, alinhado a esquerda
    texto = normaliza_nome(str(valor or ""))
    return texto[:tamanho].ljust(tamanho)


def campo_num(valor, tamanho):
    texto = so_digitos(str(valor))
    if len(texto) > tamanho:
        raise ValueError("campo numerico estoura %d posicoes: %s" % (tamanho, valor))
    return texto.rjust(tamanho, "0")


def centavos(valor):
    # 123.45 -> 12345
    return int(round(valor * 100))
