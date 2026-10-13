"""Regressão do validador da skill escrevendo-adrs: casos que devem passar e casos que devem falhar."""
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / ".agents" / "skills" / "escrevendo-adrs"
VALIDADOR = SKILL / "scripts" / "validar_adr.py"
EXEMPLO = (SKILL / "reference" / "ADR-003-armazenamento-de-alertas.md").read_text(encoding="utf-8")


def validar(tmp_path, texto, nome="ADR-003-armazenamento-de-alertas.md"):
    arquivo = tmp_path / nome
    arquivo.write_text(texto, encoding="utf-8")
    proc = subprocess.run([sys.executable, str(VALIDADOR), str(arquivo)], capture_output=True, text=True)
    return proc.returncode, proc.stdout


def test_exemplo_passa(tmp_path):
    assert validar(tmp_path, EXEMPLO)[0] == 0


def test_fixture_ruim_falha():
    proc = subprocess.run([sys.executable, str(VALIDADOR), str(SKILL / "evals" / "fixtures" / "ADR-002-cache-de-produtos.md")],
                          capture_output=True, text=True)
    assert proc.returncode == 1 and "alternativa(s)" in proc.stdout


def test_modelo_so_com_marcadores_trocados_falha(tmp_path):
    modelo = (SKILL / "reference" / "modelo-adr.md").read_text(encoding="utf-8")
    for a, b in [("ADR-NNN", "ADR-009"), ("AAAA-MM-DD", "2026-10-12"), ("Nome da alternativa", "Opção"), ("...", "x")]:
        modelo = modelo.replace(a, b)
    codigo, saida = validar(tmp_path, modelo, "ADR-009-teste.md")
    assert codigo == 1 and "quem decide (papel ou nome)" in saida


def test_palavras_com_todo_e_reticencias_no_texto_passam(tmp_path):
    texto = EXEMPLO.replace("Nenhuma dependência nova.", "TODOS os MÉTODOS seguem iguais... sem dependência nova.")
    texto = texto.replace("Adotar **A2: Tabela `alerta` no SQLite existente**.", "Adotar **A2: Tabela `alerta` no SQLite existente**, ao contrário de A1.")
    assert validar(tmp_path, texto)[0] == 0


def test_respostas_vazias_falham(tmp_path):
    casos = {
        "contras nenhum": ("- **Contras:** o campo `detalhes` (dict) vira JSON serializado; a escrita concorre com pedidos no mesmo arquivo.", "- **Contras:** nenhum."),
        "sensor vago": ("| `make check` continua sem serviço novo |", "| monitorar |"),
        "data sem hífen": ("**Data:** 2026-10-12", "**Data:** 20261012"),
        "alternativa duplicada": ("### A3: Redis com lista limitada", "### A3: Manter em memória"),
        "sem reversão": ("### Reversão", "### Outra coisa"),
        "TODO solto": ("- Nenhuma.", "- TODO"),
    }
    for nome, (a, b) in casos.items():
        assert a in EXEMPLO, nome
        assert validar(tmp_path, EXEMPLO.replace(a, b))[0] == 1, nome
