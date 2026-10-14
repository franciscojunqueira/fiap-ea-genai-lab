#!/usr/bin/env python3
"""Grava o replay do Lab 3 por `claude -p`: os 3 cenários com cada contrato e modelo. Executar.

Uso (da raiz do repositório):  python3 replay/lab3/gravar.py [<repetições>]   (padrão: 2)

Grava ruim e boa no modelo dos labs (config/modelos.toml) e no Sonnet, cada um <repetições> vezes,
em replay/lab3/gravacao/<modelo>-<versão>-<n>/. Gasta cota do plano de quem roda.
"""
import sys
import tomllib
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "labs" / "lab3"))
import comparar  # noqa: E402

MODELOS = {"haiku": tomllib.loads((RAIZ / "config" / "modelos.toml").read_text(encoding="utf-8"))["labs"]["modelo"],
           "sonnet": "sonnet"}


def main(argv):
    repeticoes = int(argv[1]) if len(argv) > 1 else 2
    for rotulo, modelo in MODELOS.items():
        for versao in ("ruim", "boa"):
            for n in range(1, repeticoes + 1):
                destino = Path(__file__).resolve().parent / "gravacao" / f"{rotulo}-{versao}-{n}"
                resumo, itens, _ = comparar.comparar(versao, modelo, destino=destino)
                resumo["grupo"] = "replay"
                print(f"{rotulo}-{versao}-{n}\t{comparar.linha(resumo)}\t" +
                      " ".join(f"{i['cenario']}={i['ajustes_pedidos']}" for i in itens), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
