# -*- coding: utf-8 -*-
# relatorio diario de inadimplencia para a area de Risco (pedido de 2016)
# provisao pela tabela de niveis de risco da Res. CMN 2.682/99, por dias de atraso
import csv
import os

from sgc import config, util

FAIXAS = [  # (atraso ate N dias, nivel, percentual de provisao)
    (14, "A", 0.005),
    (30, "B", 0.01),
    (60, "C", 0.03),
    (90, "D", 0.10),
    (120, "E", 0.30),
    (150, "F", 0.50),
    (180, "G", 0.70),
]
NIVEL_MAXIMO = ("H", 1.00)
DIAS_BAIXA = 180  # acima disso a cobranca e baixada como perda no fechamento do mes


def nivel(dias):
    for limite, nome, pct in FAIXAS:
        if dias <= limite:
            return nome, pct
    return NIVEL_MAXIMO


def _baixa_mensal(con, data_ref):
    vencidas = con.execute(
        "SELECT id, vencimento FROM cobranca WHERE status IN ('REGISTRADA', 'DIVERGENTE')"
    ).fetchall()
    n = 0
    for cob in vencidas:
        if (data_ref - util.para_data(cob["vencimento"])).days > DIAS_BAIXA:
            con.execute("UPDATE cobranca SET status = 'BAIXADA' WHERE id = ?", (cob["id"],))
            n += 1
    con.commit()
    return n


def _diretorio_saida():
    try:
        if not os.path.isdir(config.DIR_RISCO):
            os.makedirs(config.DIR_RISCO)
        return config.DIR_RISCO
    except OSError:
        if not os.path.isdir(config.DIR_RISCO_LOCAL):
            os.makedirs(config.DIR_RISCO_LOCAL)
        return config.DIR_RISCO_LOCAL


def gerar_relatorio(con, data_ref):
    if data_ref.day == 1:
        baixadas = _baixa_mensal(con, data_ref)
        util.log().info("fechamento mensal: %d cobrancas baixadas", baixadas)

    linhas = con.execute(
        "SELECT c.nosso_numero, c.valor, c.valor_pago, c.vencimento, c.status, "
        "s.documento, s.nome, s.segmento, s.saldo_devedor FROM cobranca c JOIN sacado s ON s.id = c.sacado_id "
        "WHERE c.status IN ('ABERTA', 'REGISTRADA', 'DIVERGENTE')"
    ).fetchall()

    caminho = os.path.join(_diretorio_saida(), "risco_%s.csv" % data_ref.strftime("%Y%m%d"))
    total = {"vencidas": 0, "valor_vencido": 0.0, "provisao": 0.0}
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["documento", "nome", "segmento", "nosso_numero", "em_aberto", "dias_atraso",
                    "nivel", "provisao", "saldo_devedor_sacado"])
        for l in linhas:
            dias = (data_ref - util.para_data(l["vencimento"])).days
            if dias <= 0:
                continue
            em_aberto = l["valor"] - (l["valor_pago"] or 0)
            nome_nivel, pct = nivel(dias)
            provisao = round(em_aberto * pct, 2)
            w.writerow([l["documento"], l["nome"], l["segmento"], l["nosso_numero"], "%.2f" % em_aberto,
                        dias, nome_nivel, "%.2f" % provisao, "%.2f" % l["saldo_devedor"]])
            total["vencidas"] += 1
            total["valor_vencido"] += em_aberto
            total["provisao"] += provisao
    util.log().info("relatorio de risco %s: %s", caminho, total)
    return caminho, total
