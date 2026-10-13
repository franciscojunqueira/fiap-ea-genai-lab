# -*- coding: utf-8 -*-
# processamento do arquivo de retorno do core
# ocorrencias tratadas: 02 entrada confirmada, 03 entrada rejeitada, 06 liquidacao,
#                       09 baixa, 17 liquidacao apos baixa
import datetime
import glob
import os
import shutil

from sgc import config, encargos, util

TOLERANCIA = 0.05  # diferenca de arredondamento aceita no pagamento


def _ler(caminho):
    with open(caminho, encoding="latin-1") as f:
        for linha in f:
            linha = linha.rstrip("\r\n")
            if not linha.startswith("1"):
                continue
            yield {
                "nosso_numero": linha[1:13],
                "ocorrencia": linha[13:15],
                "data": datetime.datetime.strptime(linha[15:23], "%Y%m%d").date(),
                "valor": int(linha[23:36]) / 100.0,
            }


def _liquidar(con, cob, reg, nome_arquivo, resumo):
    devido = encargos.valor_devido(cob["valor"], cob["vencimento"], reg["data"])
    status = "LIQUIDADA" if devido - reg["valor"] <= TOLERANCIA else "DIVERGENTE"
    con.execute(
        "UPDATE cobranca SET status = ?, valor_pago = ?, data_pagamento = ? WHERE id = ?",
        (status, reg["valor"], reg["data"].isoformat(), cob["id"]),
    )
    con.execute(
        "INSERT INTO pagamento (cobranca_id, valor, data, ocorrencia, arquivo) VALUES (?, ?, ?, ?, ?)",
        (cob["id"], reg["valor"], reg["data"].isoformat(), reg["ocorrencia"], nome_arquivo),
    )
    resumo[status.lower()] += 1


def processar_arquivo(con, caminho):
    nome = os.path.basename(caminho)
    if con.execute("SELECT 1 FROM arquivo_processado WHERE nome = ?", (nome,)).fetchone():
        util.log().warning("arquivo %s ja processado, ignorando", nome)
        return None

    resumo = {"registros": 0, "registradas": 0, "rejeitadas": 0, "liquidada": 0, "divergente": 0,
              "baixadas": 0, "pagas_apos_baixa": 0, "nao_encontradas": 0}
    for reg in _ler(caminho):
        resumo["registros"] += 1
        cob = con.execute("SELECT * FROM cobranca WHERE nosso_numero = ?", (reg["nosso_numero"],)).fetchone()
        if cob is None:
            resumo["nao_encontradas"] += 1
            util.log().warning("nosso numero %s nao encontrado", reg["nosso_numero"])
            continue
        oc = reg["ocorrencia"]
        if oc == "02":
            con.execute("UPDATE cobranca SET status = 'REGISTRADA' WHERE id = ? AND status = 'ABERTA'", (cob["id"],))
            resumo["registradas"] += 1
        elif oc == "03":
            con.execute("UPDATE cobranca SET status = 'REJEITADA' WHERE id = ?", (cob["id"],))
            resumo["rejeitadas"] += 1
        elif oc == "06":
            _liquidar(con, cob, reg, nome, resumo)
        elif oc == "09":
            con.execute("UPDATE cobranca SET status = 'BAIXADA' WHERE id = ?", (cob["id"],))
            resumo["baixadas"] += 1
        elif oc == "17":
            con.execute(
                "INSERT INTO pagamento (cobranca_id, valor, data, ocorrencia, arquivo) VALUES (?, ?, ?, ?, ?)",
                (cob["id"], reg["valor"], reg["data"].isoformat(), oc, nome),
            )
            resumo["pagas_apos_baixa"] += 1
        else:
            util.log().warning("ocorrencia %s desconhecida (nosso numero %s)", oc, reg["nosso_numero"])

    con.execute("INSERT INTO arquivo_processado (nome, processado_em) VALUES (?, ?)",
                (nome, datetime.datetime.now().isoformat()))
    con.commit()
    if not os.path.isdir(config.DIR_PROCESSADOS):
        os.makedirs(config.DIR_PROCESSADOS)
    shutil.move(caminho, os.path.join(config.DIR_PROCESSADOS, nome))
    util.log().info("retorno %s: %s", nome, resumo)
    return resumo


def processar_pendentes(con):
    resumos = []
    for caminho in sorted(glob.glob(os.path.join(config.DIR_RETORNO, "RET_*.txt"))):
        r = processar_arquivo(con, caminho)
        if r:
            resumos.append(r)
    return resumos
