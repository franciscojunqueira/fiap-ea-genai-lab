"""Fixtures compartilhadas pelos testes de fumaça. Cada teste usa um banco SQLite temporário."""
import pytest

from apoio_erp import erp_rodando


@pytest.fixture
def erp_url(tmp_path):
    """Sobe o Mini-ERP num processo separado, numa porta livre e com banco temporário."""
    try:
        with erp_rodando(tmp_path / "erp.db") as url:
            yield url
    except RuntimeError as erro:
        pytest.fail(str(erro))
