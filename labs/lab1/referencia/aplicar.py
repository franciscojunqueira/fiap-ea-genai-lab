#!/usr/bin/env python3
"""Aplica a solução de referência do Lab 1 (make lab1-referencia). Executar.

Plano B, quando a cota do operador acaba: troca o service e a rota de pedidos pela versão de
referência, para o grupo seguir com a verificação. Não mexe na spec, no AGENTS.md, no teste do
grupo nem no verificacao.md: esses são do grupo.

Com --exemplos (só para o teste de regressão do check), preenche também os arquivos do grupo com
os exemplos desta pasta.
"""
import re
import shutil
import sys
from pathlib import Path

REF = Path(__file__).resolve().parent
LAB = REF.parent
RAIZ = LAB.parents[1]
APP = RAIZ / "mini-erp" / "app"


def main(argv):
    if not (LAB / "spec.md").exists():
        print("Rode `make lab1` antes da referência.")
        return 1
    shutil.copy(REF / "services_pedidos.py", APP / "services" / "pedidos.py")
    shutil.copy(REF / "routes_pedidos.py", APP / "routes" / "pedidos.py")
    print("  aplicado  mini-erp/app/services/pedidos.py e mini-erp/app/routes/pedidos.py (referência)")
    if "--exemplos" in argv:
        shutil.copy(REF / "exemplo_spec.md", LAB / "spec.md")
        shutil.copy(REF / "exemplo_verificacao.md", LAB / "verificacao.md")
        shutil.copy(REF / "exemplo_test_grupo.py", LAB / "testes" / "test_grupo.py")
        sensores = LAB / "sensores.toml"
        sensores.write_text(re.sub(r"^ligado = false", "ligado = true", sensores.read_text(encoding="utf-8"), flags=re.M),
                            encoding="utf-8")
        agents = RAIZ / "AGENTS.md"
        if "## Mini-ERP" not in agents.read_text(encoding="utf-8"):
            with agents.open("a", encoding="utf-8") as f:
                f.write((REF / "exemplo_agents.md").read_text(encoding="utf-8"))
        print("  aplicado  exemplos de spec, AGENTS.md, teste do grupo, sensores e verificação")
    print("\nPróximo passo: `make lab1-check`.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
