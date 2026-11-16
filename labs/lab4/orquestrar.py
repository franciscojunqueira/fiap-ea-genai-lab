#!/usr/bin/env python3
"""Um agente × orquestrador com subagentes (Aula 3, Demonstração 1). Executar:
  make lab4-orquestrar MODO=unico        um agente revisa os 3 ADRs sozinho
  make lab4-orquestrar MODO=subagentes   o agente cria um subagente revisor para cada ADR, em paralelo
  make lab4-orquestrar-replay            mostra as duas execuções gravadas pelo professor

A tarefa é a mesma nos dois modos: revisar os 3 ADRs de labs/lab4/orquestracao/adrs/ contra o caso e
apontar o problema mais grave de cada um. Cada ADR tem um problema plantado. O script mede, por modo,
quantos problemas foram achados, quantos subagentes o agente criou, os tokens e o tempo.
Os tokens somam o agente principal e os subagentes (campo modelUsage do Claude Code).
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
import tomllib
from pathlib import Path

LAB = Path(__file__).resolve().parent
RAIZ = LAB.parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))
import cli_modelo  # noqa: E402

ADRS = LAB / "orquestracao" / "adrs"
EXECUCOES = LAB / "orquestracao" / "execucoes"
REPLAY = RAIZ / "replay" / "lab4" / "orquestracao"
# O mesmo modelo nos dois modos, para a comparação ser justa. O Sonnet coordena subagentes melhor que o Haiku.
MODELO = "claude-sonnet-5-5"
# Um modo levou até 2 min no teste; 400 s cobrem rede lenta.
TIMEOUT_S = 400
# O problema plantado em cada ADR e as palavras que mostram que o revisor o achou.
PLANTADOS = {
    "ADR-101": ("alternativa de palha (treinar um modelo do zero)",
                r"palha|espantalho|do zero|n[ãa]o [ée] (uma )?alternativa|invi[áa]vel|irreal|n[ãa]o compar[áa]vel"),
    "ADR-102": ("requisito inventado (a RC-13 não existe no caso)",
                r"RC-13[^.\n]{0,80}(n[ãa]o existe|inexistente|n[ãa]o consta|n[ãa]o h[áa]|inventad|n[ãa]o est[áa])"
                r"|(n[ãa]o existe|inexistente|inventad|n[ãa]o consta)[^.\n]{0,80}RC-13"),
    "ADR-103": ("reversão sem custo (\"basta trocar o endereço\")",
                r"revers[ãa]o[^.\n]{0,120}(sem custo|subestim|ignora|irreal|otimist|lock-?in|pol[íi]ticas)"
                r"|lock-?in|custo de (sair|sa[íi]da|voltar)"),
}
PEDIDO = {
    "unico": ("Revise os três ADRs da pasta adrs/ contra o caso em caso.md, sozinho, sem criar subagentes. "
              "Para cada ADR, diga em até 3 linhas o problema mais grave. No fim, uma tabela: ADR | problema."),
    "subagentes": ("Revise os três ADRs da pasta adrs/ contra o caso em caso.md. Use a ferramenta Agent para "
                   "criar um subagente revisor para cada ADR, os três em paralelo. Cada subagente lê só o seu ADR "
                   "e o caso.md e devolve em até 3 linhas o problema mais grave. No fim, junte os pareceres numa "
                   "tabela: ADR | problema."),
}
SISTEMA = ("Você é um revisor de arquitetura da TechCorp Banco Múltiplo. Revise ADRs contra os requisitos do "
           "caso (RC-01 a RC-12). Responda em português, em frases curtas.")


def rodar(modo):
    with tempfile.TemporaryDirectory() as pasta:
        shutil.copytree(ADRS, Path(pasta) / "adrs")
        shutil.copy(RAIZ / "integrador" / "caso.md", Path(pasta) / "caso.md")
        ferramentas = "Read,Glob,Grep" + (",Agent" if modo == "subagentes" else "")
        cmd = ["claude", "-p", PEDIDO[modo], "--model", MODELO, "--system-prompt", SISTEMA, "--tools", ferramentas,
               "--allowedTools", ferramentas, "--output-format", "stream-json", "--verbose",
               "--no-session-persistence", "--strict-mcp-config", "--restricted"]
        inicio = time.monotonic()
        try:
            proc = subprocess.run(cmd, cwd=pasta, capture_output=True, text=True, timeout=TIMEOUT_S,
                                  stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            sys.exit(f"Sem resposta em {TIMEOUT_S} s. Use make lab4-orquestrar-replay.")
        duracao = time.monotonic() - inicio
    final, subagentes = None, 0
    for linha in proc.stdout.splitlines():
        try:
            ev = json.loads(linha)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "assistant" and not ev.get("parent_tool_use_id"):
            subagentes += sum(1 for p in ev.get("message", {}).get("content", [])
                              if p.get("type") == "tool_use" and p.get("name") in ("Agent", "Task"))
        elif ev.get("type") == "result":
            final = ev
    if final is None:
        sys.exit("Resposta inesperada do Claude Code: " + (proc.stderr or proc.stdout)[-300:])
    uso = final.get("modelUsage") or {}
    tokens = sum(m.get("inputTokens", 0) + m.get("outputTokens", 0) + m.get("cacheReadInputTokens", 0)
                 + m.get("cacheCreationInputTokens", 0) for m in uso.values())
    precos = tomllib.loads((RAIZ / "config" / "modelos.toml").read_text(encoding="utf-8")).get("precos", {})
    return {"modo": modo, "modelo": MODELO, "data": time.strftime("%Y-%m-%d %H:%M"), "duracao_s": round(duracao, 1),
            "subagentes": subagentes, "tokens": tokens, "custo_usd": cli_modelo.custo_api(uso, precos),
            "texto": str(final.get("result") or ""), "erro": final.get("is_error", False)}


def achados(texto):
    return {adr: bool(re.search(rx, texto, re.I)) for adr, (_, rx) in PLANTADOS.items()}


def mostrar(r):
    ach = achados(r["texto"])
    print(f"\n=== Modo {r['modo']} ({r['modelo']}, {r['data']}) ===")
    print(r["texto"].strip()[:1800])
    print(f"\n  Subagentes criados: {r['subagentes']}")
    print(f"  Problemas plantados achados: {sum(ach.values())} de 3 "
          + " · ".join(f"{a} {'✓' if ok else '✗'}" for a, ok in ach.items()))
    custo = "?" if r["custo_usd"] is None else f"US$ {r['custo_usd']:.3f}".replace(".", ",")
    print(f"  Tokens (principal + subagentes): {r['tokens']:,}".replace(",", ".")
          + f" · tempo: {str(r['duracao_s']).replace('.', ',')} s · {custo} a preço de API")


def comparar(rs):
    if len(rs) == 2 and rs[0]["tokens"]:
        u, s = rs
        fator = lambda x: f"{x:.1f}".replace(".", ",")
        custo = (f" e {fator(s['custo_usd'] / u['custo_usd'])}× o custo (o cache barateia a releitura)"
                 if s.get("custo_usd") and u.get("custo_usd") else "")
        print(f"\nO modo com subagentes gastou {fator(s['tokens'] / u['tokens'])}× os tokens do agente único{custo}, "
              f"e levou {fator(s['duracao_s'] / max(u['duracao_s'], 0.1))}× o tempo.")
        print("Pergunta para a turma: o ganho compensou o custo, nesta tarefa?\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("modo", choices=["unico", "subagentes", "ambos", "replay"])
    a = ap.parse_args()
    if a.modo == "replay":
        rs = [json.loads((REPLAY / f"{m}.json").read_text(encoding="utf-8")) for m in ("unico", "subagentes")
              if (REPLAY / f"{m}.json").exists()]
        if not rs:
            sys.exit("Ainda não há gravação em replay/lab4/orquestracao/.")
        for r in rs:
            mostrar(r)
        comparar(rs)
        return
    msg = cli_modelo.disponivel("claude") or cli_modelo.logado()
    if msg:
        sys.exit(msg)
    EXECUCOES.mkdir(parents=True, exist_ok=True)
    rs = []
    for modo in (["unico", "subagentes"] if a.modo == "ambos" else [a.modo]):
        print(f"\nRodando o modo {modo}... (cerca de 15 s; até 2 min com rede lenta)", flush=True)
        r = rodar(modo)
        (EXECUCOES / f"{time.strftime('%Y%m%d-%H%M%S')}-{modo}.json").write_text(
            json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
        mostrar(r)
        rs.append(r)
    comparar(rs)


if __name__ == "__main__":
    main()
