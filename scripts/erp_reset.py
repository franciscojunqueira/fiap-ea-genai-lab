#!/usr/bin/env python3
"""Zera o banco do Mini-ERP (make erp-reset). Executar. É do professor: roda antes de uma demonstração.

Renomeia o banco atual com a data no nome (mini_erp-AAAAMMDD-HHMMSS.db, na mesma pasta; nada é apagado)
e recria o banco no estado inicial: 5 produtos, estoque do produto 3 em 30, nenhum ajuste, nenhum pedido.
`ERP_DB_PATH` troca o caminho do banco, como no ERP.
"""
import datetime
import os
import socket
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "mini-erp"))


def erp_no_ar(porta=8000):
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", porta)) == 0


def main():
    if erp_no_ar():
        sys.exit("O ERP está rodando na porta 8000 (make erp). Pare-o com Ctrl+C no terminal dele, rode `make erp-reset` "
                 "de novo e suba o `make erp` outra vez: com o ERP no ar, ele continuaria escrevendo no banco antigo.")
    from app.db import DB_PATH, Base, SessionLocal, engine
    from app import models, models_ajustes  # noqa: F401  (registram as tabelas)
    from app.seed import seed_db

    banco = Path(DB_PATH).resolve()
    guardado = None
    if banco.exists():
        guardado = banco.with_name(f"{banco.stem}-{datetime.datetime.now():%Y%m%d-%H%M%S}{banco.suffix}")
        engine.dispose()
        banco.rename(guardado)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_db(db)
        estoque = db.query(models.Estoque).filter_by(produto_id=3).one().quantidade
    finally:
        db.close()
    antes = f"O banco anterior ficou guardado em {guardado.name}; " if guardado else "Não havia banco anterior; "
    print(f"{antes}o banco novo está no estado inicial (estoque do produto 3 = {estoque}, nenhum ajuste). "
          "Suba o ERP com `make erp`.")


if __name__ == "__main__":
    main()
