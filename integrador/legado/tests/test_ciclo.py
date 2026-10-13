import datetime
import glob
import os
import sqlite3
import subprocess
import sys

import pytest

from sgc import banco, calendario, config, importacao, remessa, retorno, risco

LEGADO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CICLO = datetime.date(2026, 11, 25)


@pytest.fixture
def ambiente(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DIR_ENTRADA", os.path.join(LEGADO, "dados", "entrada"))
    monkeypatch.setattr(config, "DIR_REMESSA", str(tmp_path / "remessa"))
    monkeypatch.setattr(config, "DIR_RETORNO", str(tmp_path / "retorno"))
    monkeypatch.setattr(config, "DIR_PROCESSADOS", str(tmp_path / "retorno" / "processados"))
    monkeypatch.setattr(config, "DIR_RISCO", str(tmp_path / "risco"))
    con = banco.conectar(str(tmp_path / "sgc.db"))
    importacao.carregar_sacados(con, os.path.join(LEGADO, "dados", "sacados.csv"))
    return con, tmp_path


def test_calendario_2024():
    assert not calendario.eh_dia_util(datetime.date(2024, 12, 25))
    assert calendario.proximo_dia_util(datetime.date(2024, 2, 12)) == datetime.date(2024, 2, 14)


def test_importacao_csv(ambiente):
    con, _ = ambiente
    r = importacao.importar_csv(con, CICLO)
    assert r["lidas"] == 26
    assert r["cobrancas"] > 0


def test_ciclo_completo(ambiente):
    con, tmp = ambiente
    importacao.importar_csv(con, CICLO)
    caminho = remessa.gerar(con, CICLO, agora=datetime.datetime(2026, 11, 25, 10, 0))
    linhas = open(caminho, encoding="latin-1", newline="").read().split("\r\n")
    assert all(len(l) == remessa.TAMANHO_LINHA for l in linhas if l)

    simulador = os.path.join(LEGADO, "ferramentas", "simula_core.py")
    subprocess.run([sys.executable, simulador, caminho, str(tmp / "retorno")], check=True, capture_output=True)
    resumos = retorno.processar_pendentes(con)
    assert resumos and resumos[0]["liquidada"] > 0

    _, total = risco.gerar_relatorio(con, datetime.date(2027, 4, 1))
    assert total["vencidas"] > 0
    assert glob.glob(str(tmp / "risco" / "risco_*.csv"))


def test_importacao_erp(ambiente, tmp_path):
    con, _ = ambiente
    erp = tmp_path / "erp.db"
    db = sqlite3.connect(erp)
    db.executescript(
        "CREATE TABLE pedido (id INTEGER PRIMARY KEY, nome_cliente TEXT);"
        "CREATE TABLE fatura (id INTEGER PRIMARY KEY, pedido_id INTEGER, valor_total REAL, status TEXT);"
        "INSERT INTO pedido VALUES (1, 'Mercadinho Boa Vista Ltda');"
        "INSERT INTO fatura VALUES (1, 1, 250.0, 'GERADA');"
    )
    db.commit()
    db.close()
    r = importacao.importar_erp(con, CICLO, str(erp))
    assert r["cobrancas"] == 1
