#!/usr/bin/env python3
"""Prepara o Lab 1 (make lab1). Executar.

Copia os modelos do grupo (spec, verificação, sensores, teste do grupo) sem sobrescrever o que já
existe e aplica o rascunho do colega na rota de pedidos. Pode rodar de novo sem estragar nada.
"""
import shutil
from pathlib import Path

LAB = Path(__file__).resolve().parent
RAIZ = LAB.parents[1]
ROTA = RAIZ / "mini-erp" / "app" / "routes" / "pedidos.py"
MARCA = "RASCUNHO do colega"
IMPORTS_DO_RASCUNHO = "from fastapi import HTTPException\nfrom app.models import Pedido, Estoque\n"

COPIAS = {
    "modelos/spec.md": "spec.md",
    "modelos/verificacao.md": "verificacao.md",
    "modelos/sensores.toml": "sensores.toml",
    "modelos/test_grupo.py": "testes/test_grupo.py",
}


def main():
    for origem, destino in COPIAS.items():
        alvo = LAB / destino
        if alvo.exists():
            print(f"  mantido   labs/lab1/{destino} (já existia)")
            continue
        alvo.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(LAB / origem, alvo)
        print(f"  criado    labs/lab1/{destino}")

    rota = ROTA.read_text(encoding="utf-8")
    if MARCA in rota or "/cancelar" in rota:
        print("  mantido   mini-erp/app/routes/pedidos.py (o cancelamento já está lá)")
    else:
        ancora = "from app.db import get_db\n"
        rota = rota.replace(ancora, ancora + IMPORTS_DO_RASCUNHO, 1)
        rota += (LAB / "modelos" / "rascunho_do_colega.py").read_text(encoding="utf-8")
        ROTA.write_text(rota, encoding="utf-8")
        print("  aplicado  rascunho do colega em mini-erp/app/routes/pedidos.py")

    print("\nPróximo passo: `make lab1-check` (o FAIL é esperado agora) e o passo 2 de labs/lab1/README.md.")


if __name__ == "__main__":
    main()
