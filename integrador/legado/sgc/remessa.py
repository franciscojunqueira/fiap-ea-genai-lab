# -*- coding: utf-8 -*-
# geracao do arquivo de remessa para o core (layout proprietario de 200 posicoes)
# layout original em layouts/REMESSA.cpy
import datetime
import os

from sgc import banco, calendario, config, util

TAMANHO_LINHA = 200


def _header(data_remessa, sequencial):
    linha = (
        "0"
        + data_remessa.strftime("%Y%m%d")
        + util.campo_num(config.CEDENTE_AGENCIA, 4)
        + util.campo_num(config.CEDENTE_CONTA, 7)
        + util.campo_alfa(config.CEDENTE_NOME, 30)
        + util.campo_num(sequencial, 6)
    )
    return linha.ljust(TAMANHO_LINHA)


def _detalhe(cob):
    documento = util.so_digitos(cob["documento"])
    linha = (
        "1"
        + util.campo_num(cob["nosso_numero"], 12)
        + ("1" if cob["tipo"] == "F" else "2")
        + util.campo_num(documento, 14)
        + util.campo_alfa(cob["nome"], 30)
        + ("P" if cob["segmento"] == "PRIME" else "V")
        + util.para_data(cob["vencimento"]).strftime("%Y%m%d")
        + util.campo_num(util.centavos(cob["valor"]), 13)
        + util.para_data(cob["emissao"]).strftime("%Y%m%d")
        + "DM"
    )
    return linha.ljust(TAMANHO_LINHA)


def _trailer(qtd, soma_centavos):
    linha = "9" + util.campo_num(qtd, 6) + util.campo_num(soma_centavos, 17)
    return linha.ljust(TAMANHO_LINHA)


def data_da_remessa(data_ciclo, agora=None):
    agora = agora or datetime.datetime.now()
    if agora.hour >= config.HORA_CORTE:
        return calendario.proximo_dia_util(data_ciclo + datetime.timedelta(days=1))
    return data_ciclo


def gerar(con, data_ciclo, agora=None):
    cobrancas = con.execute(
        "SELECT c.*, s.nome, s.documento, s.tipo, s.segmento FROM cobranca c "
        "JOIN sacado s ON s.id = c.sacado_id WHERE c.status = 'ABERTA' AND c.remessa IS NULL ORDER BY c.id"
    ).fetchall()
    if not cobrancas:
        util.log().info("nenhuma cobranca para remessa")
        return None

    data_remessa = data_da_remessa(data_ciclo, agora)
    sequencial = banco.proximo_valor(con, "remessa")
    nome = "REM_%s_%03d.txt" % (data_remessa.strftime("%Y%m%d"), sequencial % 1000)
    if not os.path.isdir(config.DIR_REMESSA):
        os.makedirs(config.DIR_REMESSA)
    caminho = os.path.join(config.DIR_REMESSA, nome)

    linhas = [_header(data_remessa, sequencial)]
    soma = 0
    for cob in cobrancas:
        linhas.append(_detalhe(cob))
        soma += util.centavos(cob["valor"])
        con.execute("UPDATE cobranca SET remessa = ? WHERE id = ?", (nome, cob["id"]))
    linhas.append(_trailer(len(cobrancas), soma))

    with open(caminho, "w", encoding="latin-1", newline="") as f:
        f.write("\r\n".join(linhas) + "\r\n")
    con.commit()
    util.log().info("remessa %s gerada com %d cobrancas", nome, len(cobrancas))
    return caminho
