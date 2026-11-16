#!/usr/bin/env python3
"""O juiz da eval (Aula 3, Demonstração 3). Executar: make lab4-juiz PERGUNTA=P03.

O juiz é outro modelo que lê a pergunta, a resposta do Bússola e um critério escrito em frase, e diz
"certo" ou "errado" com o motivo. Ele entende o sentido, onde o script só procura palavras. Mas também
erra: por isso uma pessoa confere uma amostra do que o juiz decidiu.

Sem argumento de execução, o juiz lê a resposta da pergunta no replay do RAG do Lab 2 (Haiku), que é a
mesma que a turma viu na Aula 2: lá, o script deu a P03 como certa porque achou a palavra "Kong".
"""
import argparse
import json
import sys
import tomllib
from pathlib import Path

LAB = Path(__file__).resolve().parent
RAIZ = LAB.parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))
import cli_modelo  # noqa: E402

CASOS = tomllib.loads((LAB / "casos.toml").read_text(encoding="utf-8"))
# O juiz roda num modelo mais forte que o do Bússola (Haiku): um avaliador fraco erra mais que o avaliado.
MODELO_JUIZ = "claude-sonnet-5-5"
SISTEMA = ("Você é o juiz de uma eval. Leia a pergunta, a resposta de um assistente e o critério. Decida só pelo "
           "critério, sem usar conhecimento próprio sobre o assunto. Responda em português.")
ESQUEMA = {"type": "object", "properties": {
    "veredito": {"type": "string", "enum": ["certo", "errado"]},
    "motivo": {"type": "string"}}, "required": ["veredito", "motivo"]}
TIMEOUT_S = 120


def julgar(pergunta, resposta, criterio, cli="claude"):
    """(certo: bool | None, motivo). None quando o juiz não respondeu."""
    prompt = f"Pergunta:\n{pergunta}\n\nResposta do assistente:\n{resposta}\n\nCritério:\n{criterio}"
    r = cli_modelo.chamar(prompt, sistema=SISTEMA, modelo=MODELO_JUIZ, esquema=ESQUEMA, cli=cli, timeout_s=TIMEOUT_S)
    if r.erro or not isinstance(r.estruturado, dict):
        return None, f"o juiz não respondeu: {r.erro or 'saída sem o formato pedido'}"
    return r.estruturado.get("veredito") == "certo", str(r.estruturado.get("motivo", ""))


def resposta_do_replay(pid):
    arquivo = sorted((RAIZ / "replay" / "lab2" / "gravacao" / "haiku-rag").glob("*.json"))[-1]
    for item in json.loads(arquivo.read_text(encoding="utf-8"))["respostas"]:
        if item["id"] == pid:
            return item
    sys.exit(f"A pergunta {pid} não está no replay do Lab 2.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pergunta", nargs="?", default="P03")
    a = ap.parse_args()
    criterio = CASOS.get("juiz", {}).get(a.pergunta, {}).get("criterio")
    if not criterio:
        sys.exit(f"Não há critério do juiz para {a.pergunta} em labs/lab4/casos.toml ([juiz.{a.pergunta}]).")
    msg = cli_modelo.disponivel("claude") or cli_modelo.logado()
    if msg:
        sys.exit(msg)
    item = resposta_do_replay(a.pergunta)
    print(f"\nPergunta {a.pergunta}: {item['pergunta']}\n")
    print("Resposta do Bússola (Haiku com RAG, testes do professor, 14/10/2026):")
    print("  " + item["resposta"].replace("\n", "\n  ")[:900] + "\n")
    print(f"O SCRIPT disse: {'CERTO' if item['acerto'] else 'ERRADO'} (procurou palavras: 99,95 e ADR-001 ou Kong)")
    print(f"\nCritério do juiz:\n  {criterio}\n")
    print(f"O JUIZ ({MODELO_JUIZ}) está lendo...", flush=True)
    certo, motivo = julgar(item["pergunta"], item["resposta"], criterio)
    veredito = "não respondeu" if certo is None else ("CERTO" if certo else "ERRADO")
    print(f"O JUIZ disse: {veredito}\n  Motivo: {motivo}\n")
    print("Quem confere o juiz? Uma pessoa, numa amostra. O juiz também é um sensor que erra.\n")


if __name__ == "__main__":
    main()
