#!/usr/bin/env python3
"""Roda um ciclo de demonstração do SGC (o legado do projeto integrador). Executar: `make legado`.

Apaga e recria integrador/legado/execucao/ e roda, nesta ordem:
importar → remessa → simulador do core → retorno → relatório de risco.
Os arquivos gerados (banco, remessa, retorno, relatório) ficam em execucao/ para consulta.
Não chama modelo nenhum e não gasta cota.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

LEGADO = Path(__file__).resolve().parent.parent / "legado"
EXEC = LEGADO / "execucao"
# Data das faturas de exemplo em dados/entrada/ (faturas_20261125.csv)
DATA_CICLO = "2026-11-25"
# Dia 1 de abril de 2027: todas as cobranças já venceram e o fechamento mensal roda (sem baixas: nada passou de 180 dias)
DATA_RISCO = "2027-04-01"


def rodar(args, env):
    print("$ " + " ".join(args[1:] if args[0] == sys.executable else args))
    r = subprocess.run(args, cwd=LEGADO, env=env, capture_output=True, text=True)
    saida = (r.stdout + r.stderr).strip()
    if saida:
        print("  " + saida.replace("\n", "\n  "))
    if r.returncode != 0:
        print(f"FAIL: o passo acima saiu com código {r.returncode}. Rode `make test` para ver se o legado foi alterado.")
        sys.exit(1)


def main():
    shutil.rmtree(EXEC, ignore_errors=True)
    env = dict(os.environ,
               SGC_DB=str(EXEC / "sgc.db"),
               SGC_DIR_REMESSA=str(EXEC / "remessa"),
               SGC_DIR_RETORNO=str(EXEC / "retorno"),
               SGC_DIR_RISCO=str(EXEC / "risco"))
    py = sys.executable
    rodar([py, "-m", "sgc", "importar", "--data", DATA_CICLO], env)
    rodar([py, "-m", "sgc", "remessa", "--data", DATA_CICLO], env)
    remessa = sorted((EXEC / "remessa").glob("REM_*.txt"))
    if not remessa:
        print("FAIL: a remessa não foi gerada. Confira se dados/entrada/faturas_20261125.csv existe.")
        sys.exit(1)
    rodar([py, "ferramentas/simula_core.py", str(remessa[-1]), str(EXEC / "retorno")], env)
    rodar([py, "-m", "sgc", "retorno"], env)
    rodar([py, "-m", "sgc", "risco", "--data", DATA_RISCO], env)
    print(f"\nPASS: ciclo concluído. Banco e arquivos em {EXEC.relative_to(LEGADO.parent.parent)}/")
    print("Para olhar o banco: uv run python -m sqlite3 integrador/legado/execucao/sgc.db")
    return 0


if __name__ == "__main__":
    sys.exit(main())
