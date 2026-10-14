#!/usr/bin/env python3
"""Plano B do Lab 3 (make lab3-replay): copia as comparações gravadas para labs/lab3/comparacoes/. Executar.

Para o grupo que ficou sem cota: com as comparações ruim e boa gravadas, dá para fazer a leitura e o
contrato. A comparação do contrato do grupo (item 3 do check) e a aprovação ao vivo (item 4) não têm
replay: a aprovação não gasta cota, e a comparação do grupo leva menos de 1 min quando houver cota.
"""
import json
import shutil
from pathlib import Path

LAB = Path(__file__).resolve().parent
GRAVACAO = LAB.parents[1] / "replay" / "lab3" / "gravacao"


def main():
    destino = LAB / "comparacoes"
    destino.mkdir(exist_ok=True)
    copiadas = 0
    for arquivo in sorted(GRAVACAO.glob("*/*.json")):
        dados = json.loads(arquivo.read_text(encoding="utf-8"))
        if dados["resumo"]["versao"] not in ("ruim", "boa"):
            continue
        dados["resumo"]["grupo"] = "replay"
        nome = f"replay-{arquivo.parent.name}-{arquivo.stem}"
        (destino / f"{nome}.json").write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
        shutil.copy(arquivo.with_suffix(".md"), destino / f"{nome}.md")
        copiadas += 1
        print(f"  copiado   labs/lab3/comparacoes/{nome}.json")
    if not copiadas:
        print("Nenhuma comparação gravada em replay/lab3/gravacao/. Avisem o professor.")
        return 1
    print("\nPróximo passo: o passo 3 do README (contrato do grupo) com estas comparações.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
