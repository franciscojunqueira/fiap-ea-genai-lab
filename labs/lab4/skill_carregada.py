#!/usr/bin/env python3
"""Como uma skill é carregada (Aula 3, Demonstração 2). Executar: make lab4-skill [ou make lab4-skill-replay].

Numa pasta temporária com a skill escrevendo-adrs e o caso, o Claude Code recebe um pedido de ADR. O
script lê o passo a passo da sessão e mostra a divulgação progressiva acontecendo:
  1. no início, o agente só conhece o NOME e a DESCRIÇÃO da skill (poucas dezenas de tokens);
  2. quando o pedido combina com a descrição, ele CARREGA o corpo do SKILL.md (a ferramenta Skill);
  3. as referências e o script entram só quando um passo pede; do script, entra só a saída.
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

LAB = Path(__file__).resolve().parent
RAIZ = LAB.parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))
import cli_modelo  # noqa: E402

SKILL = RAIZ / ".agents" / "skills" / "escrevendo-adrs"
REPLAY = RAIZ / "replay" / "lab4" / "skill" / "passos.json"
MODELO = "claude-sonnet-5-5"
# A sessão levou cerca de 1 min no teste; 400 s cobrem rede lenta.
TIMEOUT_S = 400
PEDIDO = ("Registre um ADR sobre usar um AI gateway na frente dos modelos do Bússola. A decisão é usar um gateway "
          "gerenciado na região Brazil South. Use os requisitos de integrador/caso.md. Não invente decisores: marque "
          "como 'a confirmar' o que não estiver no caso.")


def descrever(nome, entrada):
    if nome == "Skill":
        return f"CARREGOU a skill {entrada.get('skill') or entrada.get('command') or ''}: o corpo do SKILL.md entrou no contexto"
    if nome == "Read":
        arq = str(entrada.get("file_path", ""))
        onde = arq.split("/skills/")[-1] if "/skills/" in arq else Path(arq).name
        return f"leu {onde}" + (" (uma referência da skill, só agora)" if "/skills/" in arq else "")
    if nome == "Bash":
        cmd = str(entrada.get("command", ""))
        return ("RODOU o validador da skill (do script, só a saída entra no contexto)" if "validar_adr" in cmd
                else f"rodou: {cmd[:80]}")
    if nome in ("Write", "Edit"):
        return f"escreveu {Path(str(entrada.get('file_path', ''))).name}"
    return f"usou {nome}"


def texto_do_resultado(parte):
    """O texto de um tool_result do stream-json (vem como texto ou como lista de partes)."""
    conteudo = parte.get("content")
    if isinstance(conteudo, list):
        return "\n".join(str(c.get("text", "")) for c in conteudo if isinstance(c, dict))
    return str(conteudo or "")


def ultimo_validador(eventos):
    """A linha [PASS] ou [FAIL] da última vez que o validador conferiu o ADR, e os erros dela."""
    ids, ultimo = set(), ""
    for ev in eventos:
        for parte in ev.get("message", {}).get("content", []) if isinstance(ev.get("message"), dict) else []:
            if not isinstance(parte, dict):
                continue
            if parte.get("type") == "tool_use" and "validar_adr" in str((parte.get("input") or {}).get("command", "")):
                ids.add(parte.get("id"))
            elif parte.get("type") == "tool_result" and parte.get("tool_use_id") in ids:
                linhas = [l for l in texto_do_resultado(parte).splitlines() if l.strip()]
                inicio = next((i for i, l in enumerate(linhas) if l.startswith(("[PASS]", "[FAIL]"))), None)
                if inicio is not None:
                    ultimo = "\n".join(linhas[inicio:inicio + 6])
    return ultimo


def rodar():
    with tempfile.TemporaryDirectory() as pasta:
        p = Path(pasta)
        shutil.copytree(SKILL, p / ".claude" / "skills" / "escrevendo-adrs")
        (p / "integrador").mkdir()
        shutil.copy(RAIZ / "integrador" / "caso.md", p / "integrador" / "caso.md")
        (p / "docs" / "adr").mkdir(parents=True)
        subprocess.run(["git", "init", "-q"], cwd=p)
        cmd = ["claude", "-p", PEDIDO, "--model", MODELO, "--permission-mode", "acceptEdits",
               "--allowedTools", "Read,Write,Edit,Glob,Grep,Bash,Skill", "--output-format", "stream-json", "--verbose",
               "--no-session-persistence", "--strict-mcp-config"]
        inicio = time.monotonic()
        try:
            proc = subprocess.run(cmd, cwd=p, capture_output=True, text=True, timeout=TIMEOUT_S, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            sys.exit(f"Sem resposta em {TIMEOUT_S} s. Use make lab4-skill-replay.")
        duracao = round(time.monotonic() - inicio, 1)
    passos, ferramentas_iniciais, eventos = [], [], []
    for linha in proc.stdout.splitlines():
        try:
            ev = json.loads(linha)
        except json.JSONDecodeError:
            continue
        eventos.append(ev)
        if ev.get("type") == "system" and ev.get("subtype") == "init":
            ferramentas_iniciais = ev.get("skills") or ev.get("slash_commands") or []
        if ev.get("type") == "assistant":
            for parte in ev.get("message", {}).get("content", []):
                if parte.get("type") == "tool_use":
                    passos.append(descrever(parte.get("name"), parte.get("input") or {}))
    return {"data": time.strftime("%Y-%m-%d %H:%M"), "modelo": MODELO, "duracao_s": duracao,
            "skills_no_inicio": ferramentas_iniciais, "passos": passos, "validador": ultimo_validador(eventos)}


def mostrar(r):
    print(f"\nPedido: {PEDIDO}\n")
    n = len(r["skills_no_inicio"])
    tem = "escrevendo-adrs" in map(str, r["skills_no_inicio"])
    print(f"No início da sessão, havia {n} skills disponíveis{' (entre elas, a escrevendo-adrs)' if tem else ''}. "
          "Do contexto, só fazem parte o NOME e a DESCRIÇÃO de cada uma.")
    print("\nO que o agente fez, na ordem:")
    for i, passo in enumerate(r["passos"], 1):
        print(f"  {i:>2}. {passo}")
    if r.get("validador"):
        print("\nO que o validador disse na última vez que conferiu o ADR:")
        for linha in r["validador"].splitlines():
            print(f"  {linha}")
    elif any("validador" in p for p in r["passos"]):
        print("\nEsta gravação não guardou a saída do validador.")
    print(f"\n({r['modelo']}, {r['data']}, {str(r['duracao_s']).replace('.', ',')} s)\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--replay", action="store_true")
    a = ap.parse_args()
    if a.replay:
        if not REPLAY.exists():
            sys.exit("Ainda não há gravação em replay/lab4/skill/.")
        return mostrar(json.loads(REPLAY.read_text(encoding="utf-8")))
    msg = cli_modelo.disponivel("claude") or cli_modelo.logado()
    if msg:
        sys.exit(msg)
    print("Rodando uma sessão com a skill escrevendo-adrs... (cerca de 1 minuto)", flush=True)
    r = rodar()
    REPLAY.parent.mkdir(parents=True, exist_ok=True)
    (LAB / "execucoes").mkdir(exist_ok=True)
    (LAB / "execucoes" / f"{time.strftime('%Y%m%d-%H%M%S')}-skill.json").write_text(
        json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    mostrar(r)


if __name__ == "__main__":
    main()
