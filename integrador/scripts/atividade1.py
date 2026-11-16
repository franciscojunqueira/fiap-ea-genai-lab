#!/usr/bin/env python3
"""Atividade 1 (engenharia reversa do SGC, opção A) em dois comandos: preparar e entregar. Executar.

    make atividade1            copia para integrador/pacote/engenharia-reversa/ a saída gravada de um
                               agente sobre o SGC (c4, dependências, regras) e o registro com 5
                               afirmações dele para o grupo conferir. Não chama modelo.
    make atividade1-entregar   roda o make er-check; com PASS, faz git add, commit e push e mostra o
                               link e o SHA para o Portal. Com FAIL, não envia nada.

Os arquivos do pacote são do grupo: o preparar só troca um arquivo que ainda está no estado do modelo
(só PREENCHER) e nunca sobrescreve o que o grupo já escreveu.
"""
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import atividade2  # noqa: E402  (o entregar é o mesmo; muda só a conferência)
from checar_entrega import sem_comentarios  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
ORIGEM = Path("integrador/atividade1/saida_agente")
DESTINO = Path("integrador/pacote/engenharia-reversa")
ARQUIVOS = ["c4.md", "dependencias.md", "regras.md", "invencoes.md"]
SEPARADOR = re.compile(r"^\|[\s:|-]+\|$")
# Linhas de estrutura do modelo que não são resposta do grupo
ESTRUTURA = {"```mermaid", "```", "flowchart LR"}


def no_estado_do_modelo(texto):
    """Verdadeiro se o arquivo só tem a estrutura do modelo e espaços PREENCHER: o grupo não escreveu nada."""
    linhas = [l.strip() for l in sem_comentarios(texto).splitlines()]
    for i, l in enumerate(linhas):
        if not l or l.startswith("#") or l in ESTRUTURA or SEPARADOR.match(l):
            continue
        if i + 1 < len(linhas) and SEPARADOR.match(linhas[i + 1]):
            continue   # cabeçalho da tabela
        resto = re.sub(r"\*\*[^*]+:\*\*", "", l).replace("PREENCHER", "")
        if re.search(r"[^\W\d_]", resto):   # sobrou alguma letra: é texto de alguém
            return False
    return "PREENCHER" in texto


def preparar(raiz=RAIZ):
    for nome in ARQUIVOS:
        origem, destino = raiz / ORIGEM / nome, raiz / DESTINO / nome
        if not origem.is_file():
            print(f"  FALTA {ORIGEM / nome}. Rodem make atualizar (responder s) e tentem de novo.")
            return 1
        if destino.exists() and not no_estado_do_modelo(destino.read_text(encoding="utf-8")):
            print(f"  mantido   {DESTINO / nome} (o grupo já escreveu nele; nada foi apagado)")
            continue
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(origem, destino)
        print(f"  preparado {DESTINO / nome}")
    faltam = sum(sem_comentarios((raiz / DESTINO / n).read_text(encoding="utf-8")).count("PREENCHER") for n in ARQUIVOS)
    print(f"""
O que isto é: a saída de um agente que fez a engenharia reversa do SGC em 08/11/2026. Ela pode ter erros.
O trabalho do grupo é conferir, não escrever tudo de novo.

Próximos passos (faltam {faltam} espaços [PREENCHER: ...]):
  1. Leiam {DESTINO}/c4.md, dependencias.md e regras.md.
  2. Em {DESTINO}/invencoes.md, conferam as 5 afirmações do agente no código e na saída do make legado.
  3. No fim de regras.md, escrevam as 3 implicações para o Bússola.
  4. No fim de invencoes.md, escrevam o que mudariam no harness.
Depois: make atividade1-entregar""")
    return 0


def entregar(raiz=RAIZ, conferir=None):
    return atividade2.entregar(raiz, conferir=conferir, etapa="er", comando="make atividade1-entregar",
                               mensagem="Atividade 1 (engenharia reversa do SGC)")


def main(argv):
    if len(argv) < 2 or argv[1] not in ("preparar", "entregar"):
        print(__doc__)
        return 2
    return preparar() if argv[1] == "preparar" else entregar()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
