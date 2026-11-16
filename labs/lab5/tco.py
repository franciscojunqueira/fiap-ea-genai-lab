#!/usr/bin/env python3
"""Custo por rota do Bússola (Aula 3, Demonstração 5). Executar: make lab5-tco [DIVISAO=<nome>].

Não chama modelo. Lê quatro coisas e faz a conta na tela:
  1. os volumes dos três cenários do caso (labs/lab5/premissas.toml);
  2. a divisão das consultas entre as arquiteturas, que é o que o gateway roteia (premissas.toml);
  3. o custo por consulta e o acerto de cada arquitetura, medidos nos testes do Lab 2 (replay/lab2/);
  4. o câmbio e o custo do gateway, com data (premissas.toml).

Conta: consultas no mês × custo por consulta da divisão + gateway, em reais, contra a RC-08.
A parcela do Risco que precisa ficar no Brasil (RC-03) sai da conta: o custo dela não foi medido.
"""
import argparse
import json
import sys
import tomllib
from pathlib import Path

LAB = Path(__file__).resolve().parent
RAIZ = LAB.parents[1]
REPLAY = RAIZ / "replay" / "lab2" / "gravacao"
NOMES = {"piloto": "Piloto", "alvo": "Alvo", "expansao": "Expansão"}


def reais(x):
    return "R$ " + f"{x:,.0f}".replace(",", ".")


def medido(arquitetura, prem):
    """(US$ por consulta, acerto em 10, estimativa?) de uma arquitetura, a partir do replay do Lab 2."""
    if arquitetura == "multiagente":
        base, _, _ = medido(prem["multiagente"]["base"], prem)
        acerto = medido(prem["multiagente"]["base"], prem)[1]
        return base * prem["multiagente"]["fator"], acerto, True
    arquivos = sorted((REPLAY / arquitetura).glob("*.json"))
    if not arquivos:
        sys.exit(f"Não achei o replay de '{arquitetura}' em replay/lab2/gravacao/. Arquiteturas: "
                 + ", ".join(sorted(p.name for p in REPLAY.iterdir() if p.is_dir())))
    r = json.loads(arquivos[-1].read_text(encoding="utf-8"))["resumo"]
    return r["usd_por_mil_perguntas"] / 1000, r["acerto"], False


def calcular(divisao, prem):
    """{cenário: (consultas na rota global, modelos R$, gateway R$, total R$)} e o custo médio em US$ por consulta."""
    div = {k: v for k, v in prem["divisao"][divisao].items() if k != "descricao"}
    usd = sum(f * medido(a, prem)[0] for a, f in div.items())
    cambio, dias = prem["cambio"]["usd_brl"], prem["volumes"]["dias_uteis_mes"]
    infra = prem["infra"]["gateway_usd_mes"] * cambio
    saida = {}
    for cen in ("piloto", "alvo", "expansao"):
        glob = prem["volumes"][cen] - prem["residencia"][cen]
        modelos = glob * dias * usd * cambio
        saida[cen] = (glob, modelos, infra, modelos + infra)
    return saida, usd


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--divisao", default="roteado")
    ap.add_argument("--premissas", default=str(LAB / "premissas.toml"))
    a = ap.parse_args()
    prem = tomllib.loads(Path(a.premissas).read_text(encoding="utf-8"))
    if a.divisao not in prem["divisao"]:
        sys.exit(f"Divisão '{a.divisao}' não existe. Opções: {', '.join(prem['divisao'])}")
    div = {k: v for k, v in prem["divisao"][a.divisao].items() if k != "descricao"}
    if abs(sum(div.values()) - 1) > 1e-6:
        sys.exit(f"As frações da divisão '{a.divisao}' somam {sum(div.values())}, e não 1.")
    cambio, gateway = prem["cambio"]["usd_brl"], prem["infra"]["gateway_usd_mes"]
    dias = prem["volumes"]["dias_uteis_mes"]

    print(f"\nDivisão: {a.divisao} — {prem['divisao'][a.divisao]['descricao']}\n")
    print("1. Custo por consulta de cada arquitetura (medido nos testes do Lab 2, a preço de API):")
    usd_consulta = 0.0
    for arq, frac in div.items():
        custo, acerto, est = medido(arq, prem)
        usd_consulta += frac * custo
        marca = "  ESTIMATIVA" if est else ""
        txt_acerto = "acerto não medido" if est else f"acerto {acerto}/10"
        print(f"   {arq:<16} US$ {custo * 1000:>6.2f} por mil · {txt_acerto} · {frac:.0%} das consultas{marca}"
              .replace(".", ","))
    print(f"   Média da divisão: US$ {usd_consulta * 1000:.2f} por mil consultas".replace(".", ","))
    print(f"\n2. Premissas: {dias} dias úteis por mês; câmbio R$ {f'{cambio:.4f}'.replace('.', ',')} "
          f"(PTAX de {prem['cambio']['data']}); gateway US$ {gateway} por mês.\n")

    print("3. Custo por mês")
    print(f"   {'Cenário':<9} {'Consultas/dia':>13} {'na rota global':>14} {'Modelos':>11} {'Gateway':>9} "
          f"{'Total':>11}  RC-08 (R$ 35 mil no alvo)")
    for cen in ("piloto", "alvo", "expansao"):
        vol = prem["volumes"][cen]
        brasil = prem["residencia"][cen]
        glob = vol - brasil
        modelos = glob * dias * usd_consulta * cambio
        infra = gateway * cambio
        total = modelos + infra
        if cen == "alvo":
            folga = (total / prem["orcamento"]["alvo_brl"] - 1) * 100
            veredito = (f"cabe ({abs(folga):.0f}% abaixo)" if total <= prem["orcamento"]["alvo_brl"]
                        else f"NÃO cabe ({folga:.1f}% acima)").replace(".", ",")
        else:
            veredito = "sem orçamento no caso"
        print(f"   {NOMES[cen]:<9} {vol:>13,} {glob:>14,} {reais(modelos):>11} {reais(infra):>9} {reais(total):>11}"
              .replace(",", ".") + f"  {veredito}")
    print("\n4. Fora da conta: a rota no Brasil (RC-03). O Risco faz 450 consultas por dia útil com dado pessoal.")
    print("   Também fora: a observabilidade, os 5 anos de registro (RC-05) e o juiz em produção. Todo \"cabe\" é otimista.")
    print("   Nenhum Claude roda no Brasil (16/11/2026): o custo dessa rota não foi medido e pode inverter a decisão.")
    print("\nPergunta para a turma: go ou no-go em cada cenário? E o que inverteria a decisão?\n")


if __name__ == "__main__":
    main()
