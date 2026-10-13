# -*- coding: utf-8 -*-
# uso: python -m sgc <etapa> [--data AAAA-MM-DD] [--origem csv|erp]
#   etapas: importar, remessa, retorno, risco, notificar, ciclo (todas, na ordem do lote noturno)
import argparse
import datetime
import os
import sys

from sgc import banco, config, importacao, notificacao, remessa, retorno, risco, util

ETAPAS = ["importar", "remessa", "retorno", "risco", "notificar", "ciclo"]


def main(argv=None):
    p = argparse.ArgumentParser(prog="sgc")
    p.add_argument("etapa", choices=ETAPAS)
    p.add_argument("--data", help="data do ciclo (padrao: hoje)")
    p.add_argument("--origem", choices=["csv", "erp"], default="csv")
    args = p.parse_args(argv)

    data_ciclo = util.para_data(args.data) if args.data else datetime.date.today()
    con = banco.conectar()
    importacao.carregar_sacados(con, os.path.join(config.BASE_DIR, "dados", "sacados.csv"))

    if args.etapa in ("importar", "ciclo"):
        if args.origem == "erp":
            r = importacao.importar_erp(con, data_ciclo)
        else:
            r = importacao.importar_csv(con, data_ciclo)
        util.log().info("importacao: %s", r)
    if args.etapa in ("remessa", "ciclo"):
        remessa.gerar(con, data_ciclo)
    if args.etapa in ("retorno", "ciclo"):
        retorno.processar_pendentes(con)
    if args.etapa in ("risco", "ciclo"):
        risco.gerar_relatorio(con, data_ciclo)
    if args.etapa in ("notificar", "ciclo"):
        notificacao.avisar_atrasados(con, data_ciclo)
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
