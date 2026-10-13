# -*- coding: utf-8 -*-
# importacao das faturas a cobrar
#   origem CSV: arquivo faturas_AAAAMMDD.csv deixado pelos sistemas de origem em DIR_ENTRADA
#   origem ERP: leitura direta do banco do ERP do Gestao PJ (desde 2022)
import csv
import datetime
import os
import sqlite3

from sgc import calendario, config, nosso_numero, util


def carregar_sacados(con, caminho):
    if con.execute("SELECT COUNT(*) FROM sacado").fetchone()[0] > 0:
        return 0
    n = 0
    with open(caminho, encoding="latin-1") as f:
        for linha in csv.DictReader(f, delimiter=";"):
            con.execute(
                "INSERT INTO sacado (nome, nome_normalizado, documento, tipo, segmento, telefone) VALUES (?, ?, ?, ?, ?, ?)",
                (linha["nome"], util.normaliza_nome(linha["nome"]), linha["documento"], linha["tipo"],
                 linha["segmento"] or "VAREJO", linha["telefone"]),
            )
            n += 1
    con.commit()
    return n


def _sacado_por_nome(con, nome):
    return con.execute(
        "SELECT * FROM sacado WHERE nome_normalizado = ? ORDER BY id LIMIT 1", (util.normaliza_nome(nome),)
    ).fetchone()


def calcula_vencimento(data_ciclo, segmento):
    prazo = config.PRAZO_PRIME_DIAS if segmento == "PRIME" else config.PRAZO_PADRAO_DIAS
    return calendario.proximo_dia_util(data_ciclo + datetime.timedelta(days=prazo))


def _registrar(con, origem, origem_id, cliente, valor, data_ciclo, resumo):
    sacado = _sacado_por_nome(con, cliente)
    if sacado is None:
        util.log().warning("sacado nao encontrado: %s (fatura %s)", cliente, origem_id)
        resumo["ignoradas"] += 1
        return

    pendentes = con.execute(
        "SELECT id, valor FROM pendente_agrupamento WHERE sacado_id = ?", (sacado["id"],)
    ).fetchall()
    total = valor + sum(p["valor"] for p in pendentes)
    if total < config.VALOR_MINIMO_BOLETO:
        con.execute(
            "INSERT INTO pendente_agrupamento (sacado_id, origem, origem_id, valor, criado_em) VALUES (?, ?, ?, ?, ?)",
            (sacado["id"], origem, origem_id, valor, data_ciclo.isoformat()),
        )
        resumo["acumuladas"] += 1
        return

    con.execute(
        "INSERT INTO cobranca (nosso_numero, sacado_id, origem, origem_id, valor, emissao, vencimento) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (nosso_numero.gerar(con), sacado["id"], origem, origem_id, round(total, 2), data_ciclo.isoformat(),
         calcula_vencimento(data_ciclo, sacado["segmento"]).isoformat()),
    )
    if pendentes:
        con.execute("DELETE FROM pendente_agrupamento WHERE sacado_id = ?", (sacado["id"],))
    resumo["cobrancas"] += 1


def importar_csv(con, data_ciclo):
    caminho = os.path.join(config.DIR_ENTRADA, "faturas_%s.csv" % data_ciclo.strftime("%Y%m%d"))
    resumo = {"lidas": 0, "cobrancas": 0, "acumuladas": 0, "ignoradas": 0}
    if not os.path.exists(caminho):
        util.log().info("sem arquivo de faturas para %s", data_ciclo)
        return resumo
    with open(caminho, encoding="latin-1") as f:
        for linha in csv.DictReader(f, delimiter=";"):
            resumo["lidas"] += 1
            valor = float(linha["valor"].replace(".", "").replace(",", "."))
            _registrar(con, linha["sistema"], linha["fatura"], linha["cliente"], valor, data_ciclo, resumo)
    con.commit()
    return resumo


def importar_erp(con, data_ciclo, caminho_erp=None):
    caminho_erp = caminho_erp or config.ERP_DB
    resumo = {"lidas": 0, "cobrancas": 0, "acumuladas": 0, "ignoradas": 0}
    erp = sqlite3.connect(caminho_erp)
    erp.row_factory = sqlite3.Row
    faturas = erp.execute(
        "SELECT f.id, f.valor_total, p.nome_cliente FROM fatura f "
        "JOIN pedido p ON p.id = f.pedido_id WHERE f.status = 'GERADA'"
    ).fetchall()
    for fat in faturas:
        resumo["lidas"] += 1
        _registrar(con, "ERP", str(fat["id"]), fat["nome_cliente"], fat["valor_total"], data_ciclo, resumo)
        erp.execute("UPDATE fatura SET status = 'EM_COBRANCA' WHERE id = ?", (fat["id"],))
    con.commit()
    erp.commit()
    erp.close()
    return resumo
