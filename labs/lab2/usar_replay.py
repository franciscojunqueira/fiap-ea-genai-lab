#!/usr/bin/env python3
"""Plano B do Lab 2 (make lab2-replay): copia execuções gravadas para labs/lab2/execucoes/. Executar.

Para o grupo que ficou sem cota: com as execuções gravadas, dá para fazer a verificação e a decisão.
Copia os dois pipelines no modelo dos labs e a variação acl = "prompt". Na planilha, a linha sai com
"replay" no lugar do nome do grupo, e o professor vê que o grupo usou o plano B.
"""
import json
import shutil
from pathlib import Path

LAB = Path(__file__).resolve().parent
GRAVACAO = LAB.parents[1] / "replay" / "lab2" / "gravacao"


def main():
    destino = LAB / "execucoes"
    destino.mkdir(exist_ok=True)
    copiadas = 0
    for arquivo in sorted(GRAVACAO.glob("*/*.json")):
        dados = json.loads(arquivo.read_text(encoding="utf-8"))
        if dados["resumo"]["pipeline"] not in ("rag", "agentica") or dados["resumo"]["variacao"] not in ("padrão", "acl=prompt"):
            continue
        dados["resumo"]["grupo"] = "replay"
        nome = f"replay-{arquivo.parent.name}-{arquivo.stem}"
        (destino / f"{nome}.json").write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
        shutil.copy(arquivo.with_suffix(".md"), destino / f"{nome}.md")
        copiadas += 1
        print(f"  copiado   labs/lab2/execucoes/{nome}.json")
    if not copiadas:
        print("Nenhuma execução gravada em replay/lab2/gravacao/. Avisem o professor.")
        return 1
    print("\nPróximo passo: `make lab2-check` e os passos 4 e 5 do README com estas execuções.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
