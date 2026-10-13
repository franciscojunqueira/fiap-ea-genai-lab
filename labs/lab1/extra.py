#!/usr/bin/env python3
"""Desafio extra do Lab 1 (make lab1-extra): a skill escrevendo-adrs sem e com, no Haiku. Executar.

Roda o cenário 2 da skill ("Crie um ADR para migrar o banco do Mini-ERP de SQLite para
PostgreSQL", sem decisores nem requisitos) duas vezes, numa cópia limpa: sem a skill e com ela.
Depois mostra, lado a lado, o que cada execução escreveu nos pontos em que o Haiku costuma inventar,
e o checklist do cenário para o verificador marcar. Gasta 2 execuções da cota do operador.

Com --de-novo, roda só a condição "com" (para medir depois de ajustar a skill: ciclo completo).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SKILL, CENARIO, MODELO = "escrevendo-adrs", 2, "haiku"
CAMPOS = re.compile(r"^\*\*(Decisores|Status):\*\*.*$|^\| RQ-\d{2} .*$|^## Pendências$", re.MULTILINE)


def rodar(sem: bool):
    args = [sys.executable, "scripts/testar_skill.py", SKILL, str(CENARIO), MODELO] + (["--sem"] if sem else [])
    print(f"\n>>> {'sem' if sem else 'com'} a skill (leva de 40 s a 90 s; medido em 12/10/2026)", flush=True)
    proc = subprocess.run(args, cwd=RAIZ, capture_output=True, text=True)
    print(proc.stdout.strip() or proc.stderr.strip()[-400:])
    return RAIZ / "resultados" / f"{SKILL}-c{CENARIO}-{MODELO}-{'sem' if sem else 'com'}-r1"


def resumo(pasta: Path):
    adrs = sorted((pasta / "arquivos").rglob("*.md")) if (pasta / "arquivos").exists() else []
    adrs = [a for a in adrs if a.name != "README.md"]
    if not adrs:
        return ["(nenhum ADR escrito)"]
    texto = adrs[0].read_text(encoding="utf-8")
    linhas = [m.group(0) for m in CAMPOS.finditer(texto)]
    fora = [str(a.relative_to(pasta / "arquivos")) for a in (pasta / "arquivos").rglob("*")
            if a.is_file() and not str(a.relative_to(pasta / "arquivos")).startswith("docs/adr/")]
    return [f"arquivo: {adrs[0].name}"] + linhas + ([f"alterou fora de docs/adr/: {', '.join(fora)}"] if fora else [])


def main(argv):
    condicoes = [False] if "--de-novo" in argv else [True, False]
    pastas = {sem: rodar(sem) for sem in condicoes}
    for sem, pasta in pastas.items():
        print(f"\n=== {'SEM' if sem else 'COM'} a skill: o que conferir ===")
        for linha in resumo(pasta):
            print(f"  {linha}")
        print(f"  (resposta completa em {pasta.relative_to(RAIZ)}/resposta.md)")
    cenario = json.loads((RAIZ / ".agents/skills" / SKILL / "evals/cenarios.json").read_text(encoding="utf-8"))[CENARIO - 1]
    print("\n=== Checklist do verificador (marque cada item nas duas condições) ===")
    for item in cenario["expected_behavior"]:
        print(f"  [ ] {item}")
    print("\nPergunta: o Haiku inventou decisores, volumes ou requisitos? Se sim, que linha da skill vocês mudariam?"
          "\nAjustem .agents/skills/escrevendo-adrs/SKILL.md e rodem `make lab1-extra ARGS=--de-novo`.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
