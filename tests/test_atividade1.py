"""Atividade 1 (opção A): o preparar copia a saída do agente sem sobrescrever o grupo; o er-check reprova
com PREENCHER e passa preenchido; o entregar só envia com PASS."""
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "integrador" / "scripts"))
import atividade1  # noqa: E402
sys.path.insert(0, str(RAIZ / "integrador" / "scripts"))

ER = Path("integrador/pacote/engenharia-reversa")
SAIDA = RAIZ / "integrador" / "atividade1" / "saida_agente"
# Os testes que partem dos modelos do pacote conferem o template. Depois do `make atividade1` (repositório de grupo),
# os arquivos já têm a saída do agente: pular em vez de falhar, para o `make test` do grupo não acusar erro que não é dele.
so_no_template = pytest.mark.skipif(
    not all(atividade1.no_estado_do_modelo((RAIZ / ER / n).read_text(encoding="utf-8")) for n in atividade1.ARQUIVOS),
    reason="Atividade 1 já preparada: estes testes conferem os modelos do template")


@pytest.fixture
def repo(tmp_path):
    """Um repositório de grupo no estado do template: modelos do pacote, a saída gravada, o legado e o caso."""
    shutil.copytree(RAIZ / "integrador" / "legado", tmp_path / "integrador" / "legado",
                    ignore=shutil.ignore_patterns("execucao", "__pycache__", "saida", "dados/sgc.db"))
    shutil.copytree(RAIZ / "integrador" / "atividade1", tmp_path / "integrador" / "atividade1")
    (tmp_path / "integrador" / "pacote").mkdir(parents=True)
    for nome in atividade1.ARQUIVOS:   # os modelos do pacote, como o template os entrega
        (tmp_path / ER).mkdir(parents=True, exist_ok=True)
        shutil.copy(RAIZ / ER / nome, tmp_path / ER / nome)
    shutil.copy(RAIZ / "integrador" / "caso.md", tmp_path / "integrador" / "caso.md")
    return tmp_path


def er_check(raiz):
    r = subprocess.run([sys.executable, str(RAIZ / "integrador/scripts/checar_entrega.py"), "er", str(raiz)],
                       capture_output=True, text=True)
    return r.returncode, r.stdout


VEREDITO_PREENCHER = "[PREENCHER: correto, errado, impreciso ou não verificável]"


def preencher(raiz, veredito_1="correto", corrigir=True):
    """O que o grupo faz no formato novo: troca cada [PREENCHER: ...] por uma resposta de verdade. A afirmação 1 recebe
    `veredito_1`; se for errado ou impreciso e `corrigir`, o c4.md (arquivo de origem) ganha a nota da correção."""
    for nome in atividade1.ARQUIVOS:
        arquivo = raiz / ER / nome
        texto = arquivo.read_text(encoding="utf-8")
        texto = texto.replace(VEREDITO_PREENCHER, veredito_1, 1).replace(VEREDITO_PREENCHER, "correto")
        texto = texto.replace("[PREENCHER: o que vocês leram ou rodaram, e o que viram]", "li sgc/importacao.py:85 e rodei `make legado`")
        arquivo.write_text(re.sub(r"\[PREENCHER:[^\]]*\]", "resposta do grupo", texto), encoding="utf-8")
    if veredito_1 in ("errado", "impreciso") and corrigir:
        c4 = raiz / ER / "c4.md"
        c4.write_text(c4.read_text(encoding="utf-8") + "\n> corrigido pelo verificador: o CSV também traz Gestão PJ.\n", encoding="utf-8")


@so_no_template
def test_modelo_do_template_e_reconhecido_e_a_saida_do_agente_nao():
    for nome in atividade1.ARQUIVOS:
        assert atividade1.no_estado_do_modelo((RAIZ / ER / nome).read_text(encoding="utf-8")), nome
        assert not atividade1.no_estado_do_modelo((SAIDA / nome).read_text(encoding="utf-8")), nome


@so_no_template
def test_preparar_copia_a_saida_gravada_e_deixa_os_preencher(repo, capsys):
    assert atividade1.preparar(repo) == 0
    for nome in atividade1.ARQUIVOS:
        assert (repo / ER / nome).read_bytes() == (SAIDA / nome).read_bytes()
    assert "preparado" in capsys.readouterr().out
    regras = (repo / ER / "regras.md").read_text(encoding="utf-8")
    implicacoes = regras.split("## Implicações para o Bússola")[1]
    assert implicacoes.count("[PREENCHER:") >= 3
    inv = (repo / ER / "invencoes.md").read_text(encoding="utf-8")
    assert inv.count("| [PREENCHER: o que vocês leram") == 5 and "## O que mudaríamos no harness" in inv
    assert "pode conter erros" in (repo / ER / "c4.md").read_text(encoding="utf-8").splitlines()[0]


@so_no_template
def test_preparar_nunca_sobrescreve_o_que_o_grupo_escreveu(repo, capsys):
    atividade1.preparar(repo)
    regras = repo / ER / "regras.md"
    do_grupo = regras.read_text(encoding="utf-8").replace("[PREENCHER: implicação 1.", "O Bússola só lê.[PREENCHER: implicação 1.", 1)
    regras.write_text(do_grupo, encoding="utf-8")
    capsys.readouterr()
    assert atividade1.preparar(repo) == 0   # rodar de novo
    assert regras.read_text(encoding="utf-8") == do_grupo
    assert "mantido" in capsys.readouterr().out
    # um arquivo que o grupo escreveu do zero também fica
    (repo / ER / "c4.md").write_text("# C4\n\nO nosso diagrama.\n", encoding="utf-8")
    atividade1.preparar(repo)
    assert (repo / ER / "c4.md").read_text(encoding="utf-8") == "# C4\n\nO nosso diagrama.\n"


@so_no_template
def test_er_check_reprova_com_preencher_e_passa_preenchido(repo):
    atividade1.preparar(repo)
    codigo, saida = er_check(repo)
    assert codigo == 1 and "PREENCHER" in saida
    for nome in ("regras.md", "invencoes.md"):   # onde o grupo escreve
        assert f"engenharia-reversa/{nome}: ainda há" in saida
    preencher(repo)
    codigo, saida = er_check(repo)
    assert codigo == 0, saida
    assert "PASS (engenharia reversa)" in saida


@so_no_template
def test_er_check_reprova_se_sobrar_um_preencher_so(repo):
    atividade1.preparar(repo)
    preencher(repo)
    inv = repo / ER / "invencoes.md"
    antes, _, depois = inv.read_text(encoding="utf-8").rpartition("resposta do grupo")   # a última, fora do comentário
    inv.write_text(antes + "[PREENCHER: veredito]" + depois, encoding="utf-8")
    codigo, saida = er_check(repo)
    assert codigo == 1 and "ainda há 1 'PREENCHER'" in saida


def test_as_cinco_afirmacoes_citam_linhas_que_existem_e_a_dica_nao_entrega_o_veredito():
    inv = (SAIDA / "invencoes.md").read_text(encoding="utf-8")
    linhas = [l for l in inv.splitlines() if re.match(r"\| \d \|", l)]
    assert len(linhas) == 5
    for l in linhas:
        _, n, afirmacao, dica, como, veredito, _ = (c.strip() for c in l.split("|"))
        arquivo, numero = re.search(r"`(\w+\.md):(\d+)`", afirmacao).groups()
        texto = (SAIDA / arquivo).read_text(encoding="utf-8").splitlines()
        assert int(numero) <= len(texto)
        assert como.startswith("[PREENCHER:") and veredito.startswith("[PREENCHER:")
        assert dica == f"Abram `{arquivo}` e rodem `make legado`.", dica   # uniforme e neutra nas 5 linhas
        assert not re.search(r"errad|inventad|impreciso|incorret|falso|correto", dica, re.I), dica
    # as linhas citadas dizem o que a afirmação diz
    assert "Gestão PJ não entra por CSV" in (SAIDA / "c4.md").read_text(encoding="utf-8").splitlines()[117]
    assert "SGC-WS" in (SAIDA / "dependencias.md").read_text(encoding="utf-8").splitlines()[15]
    assert "Calendário só conhece" in (SAIDA / "regras.md").read_text(encoding="utf-8").splitlines()[14]
    assert "nome normalizado" in (SAIDA / "regras.md").read_text(encoding="utf-8").splitlines()[16]
    assert "não é somente leitura" in (SAIDA / "regras.md").read_text(encoding="utf-8").splitlines()[27]


def _repo_com_remoto(tmp_path):
    def g(pasta, *args):
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=pasta, check=True, capture_output=True)
    remoto, repo = tmp_path / "remoto.git", tmp_path / "repo"
    g(tmp_path, "init", "-q", "--bare", "-b", "main", str(remoto))
    g(tmp_path, "init", "-q", "-b", "main", str(repo))
    (repo / "a.txt").write_text("1\n", encoding="utf-8")
    g(repo, "add", "-A")
    g(repo, "commit", "-q", "-m", "inicio")
    g(repo, "remote", "add", "origin", str(remoto))
    g(repo, "push", "-q", "-u", "origin", "main")
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=repo, check=True)
    return repo, remoto


def test_entregar_nao_envia_com_fail_e_envia_com_pass(tmp_path, capsys):
    repo, remoto = _repo_com_remoto(tmp_path)
    (repo / "b.txt").write_text("2\n", encoding="utf-8")
    assert atividade1.entregar(repo, conferir=lambda: 1) == 1
    out = capsys.readouterr().out
    assert "Nada foi enviado" in out and "make atividade1-entregar" in out
    assert subprocess.run(["git", "log", "--oneline"], cwd=remoto, capture_output=True, text=True).stdout.count("\n") == 1
    assert atividade1.entregar(repo, conferir=lambda: 0) == 0
    sha = subprocess.run(["git", "rev-parse", "main"], cwd=remoto, capture_output=True, text=True).stdout.strip()
    out = capsys.readouterr().out
    assert f"SHA:  {sha}" in out and "link:" in out
    assert "Atividade 1" in subprocess.run(["git", "log", "-1", "--format=%s"], cwd=remoto, capture_output=True, text=True).stdout


@so_no_template
def test_entregar_com_o_er_check_de_verdade_reprova_o_modelo_vazio(repo, capsys):
    """Sem conferir injetado: o entregar chama o er-check do repositório."""
    (repo / "integrador/scripts").mkdir(parents=True)
    shutil.copy(RAIZ / "integrador/scripts/checar_entrega.py", repo / "integrador/scripts/checar_entrega.py")
    assert atividade1.entregar(repo) == 1
    assert "Nada foi enviado" in capsys.readouterr().out


# ----- o check mais forte do formato novo, e o formato antigo que continua passando -------------------------------

@so_no_template
def test_formato_novo_errado_so_passa_com_a_correcao_no_arquivo_de_origem(repo):
    atividade1.preparar(repo)
    preencher(repo, veredito_1="errado", corrigir=False)
    codigo, saida = er_check(repo)
    assert codigo == 1 and "c4.md" in saida and "corrigido pelo verificador" in saida
    c4 = repo / ER / "c4.md"
    c4.write_text(c4.read_text(encoding="utf-8") + "\n> corrigido pelo verificador: o CSV também traz Gestão PJ.\n", encoding="utf-8")
    codigo, saida = er_check(repo)
    assert codigo == 0, saida


@so_no_template
def test_formato_novo_impreciso_tambem_exige_a_correcao(repo):
    atividade1.preparar(repo)
    preencher(repo, veredito_1="impreciso", corrigir=False)
    assert er_check(repo)[0] == 1
    preencher_nota = repo / ER / "c4.md"
    preencher_nota.write_text(preencher_nota.read_text(encoding="utf-8") + "\n(Corrigido pelo verificador.)\n", encoding="utf-8")
    assert er_check(repo)[0] == 0


@so_no_template
def test_formato_novo_veredito_fora_do_vocabulario_reprova(repo):
    atividade1.preparar(repo)
    preencher(repo, veredito_1="inventado")
    codigo, saida = er_check(repo)
    assert codigo == 1 and "o veredito 'inventado' não é um destes" in saida


@so_no_template
def test_formato_novo_aceita_nao_verificavel_e_exige_evidencia_e_tres_implicacoes(repo):
    atividade1.preparar(repo)
    preencher(repo, veredito_1="não verificável")
    assert er_check(repo)[0] == 0
    inv = repo / ER / "invencoes.md"
    original = inv.read_text(encoding="utf-8")
    inv.write_text(original.replace("li sgc/importacao.py:85 e rodei `make legado`", "olhamos e parece certo", 1), encoding="utf-8")
    codigo, saida = er_check(repo)
    assert codigo == 1 and "afirmação 1: 'Como conferimos' precisa citar" in saida
    inv.write_text(original, encoding="utf-8")
    regras = repo / ER / "regras.md"
    texto = regras.read_text(encoding="utf-8")
    regras.write_text(texto.replace("- resposta do grupo\n", "", 2), encoding="utf-8")
    codigo, saida = er_check(repo)
    assert codigo == 1 and "1 implicação(ões) para o Bússola; o mínimo é 3" in saida


def _repo_no_formato_antigo(tmp_path):
    """O que um grupo da turma de outubro entregou: invencoes.md de 4 colunas, veredito 'inventado', sem correção."""
    repo = tmp_path / "antigo"
    shutil.copytree(RAIZ / "integrador" / "legado", repo / "integrador" / "legado",
                    ignore=shutil.ignore_patterns("execucao", "__pycache__", "saida", "dados/sgc.db"))
    (repo / ER).mkdir(parents=True)
    for nome in ("c4.md", "dependencias.md", "regras.md"):
        shutil.copy(SAIDA / nome, repo / ER / nome)
    regras = repo / ER / "regras.md"
    regras.write_text(re.sub(r"\[PREENCHER:[^\]]*\]", "uma implicação", regras.read_text(encoding="utf-8")), encoding="utf-8")
    linhas = "\n".join(f"| {i} | afirmação {i} | olhamos | {v} |" for i, v in enumerate(["inventado", "correto", "impreciso", "correto", "não verificável"], 1))
    (repo / ER / "invencoes.md").write_text(
        "# Registro\n\n**Agente e modelo usados:** Claude\n\n| # | O que o agente afirmou | Como o grupo conferiu | Veredito |\n|---|---|---|---|\n"
        + linhas + "\n\n## O que mudaríamos no harness\n\n- mais testes\n", encoding="utf-8")
    shutil.copy(RAIZ / "integrador" / "caso.md", repo / "integrador" / "caso.md")
    return repo


def test_formato_antigo_continua_passando_como_antes(tmp_path):
    repo = _repo_no_formato_antigo(tmp_path)
    codigo, saida = er_check(repo)
    assert codigo == 0, saida
    assert "PASS (engenharia reversa)" in saida


def test_o_modelo_do_pacote_novo_e_o_antigo_se_distinguem_pelo_cabecalho():
    from checar_entrega import FORMATO_NOVO
    assert FORMATO_NOVO.search((SAIDA / "invencoes.md").read_text(encoding="utf-8"))
    assert not FORMATO_NOVO.search("| # | O que o agente afirmou | Como o grupo conferiu | Veredito |\n|---|---|---|---|\n")
