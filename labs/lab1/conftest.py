"""Fixture erp_url para os testes do Lab 1 (aceite e grupo): o Mini-ERP com banco temporário."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests"))
from apoio_erp import erp_rodando  # noqa: E402


@pytest.fixture
def erp_url(tmp_path):
    try:
        with erp_rodando(tmp_path / "erp.db") as url:
            yield url
    except RuntimeError as erro:
        pytest.fail(str(erro))
