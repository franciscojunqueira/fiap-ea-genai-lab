#!/usr/bin/env python3
"""Fitness function 'camadas' do Mini-ERP. Executar (o make lab1-check chama; roda sozinha também).

Regras, conferidas na árvore sintática do código (não por texto):
  - rotas (mini-erp/app/routes/) não importam app.models nem acessam o banco
    (db.query, add, commit, flush, delete, refresh, rollback, execute, merge): chamam um service;
  - services (mini-erp/app/services/) não importam o FastAPI: levantam os erros de services/erros.py.
Arquivos em `excecoes` (labs/lab1/sensores.toml) ficam de fora: são dívida registrada.
Código de saída 1 se houver violação.
"""
import ast
import sys
import tomllib
from pathlib import Path

LAB = Path(__file__).resolve().parent
APP = LAB.parents[1] / "mini-erp" / "app"
ACESSO_AO_BANCO = {"query", "add", "add_all", "commit", "flush", "delete", "refresh", "rollback", "execute", "merge"}
# De app.db a rota só precisa da dependência que injeta a sessão; de sqlalchemy, só o tipo Session.
PERMITIDO_NA_ROTA = {"app.db": {"get_db"}, "sqlalchemy.orm": {"Session"}}


def violacoes_da_rota(arquivo: Path) -> list[str]:
    rel = arquivo.relative_to(APP.parent.parent)
    servico = f"mini-erp/app/services/{arquivo.name}"
    achados = []
    for no in ast.walk(ast.parse(arquivo.read_text(encoding="utf-8"))):
        if isinstance(no, ast.Import):
            # `import app.models as m` e `import sqlalchemy` contam como importar o modelo ou o banco
            for alias in no.names:
                if alias.name.startswith(("app.models", "app.db", "sqlalchemy")):
                    achados.append(f"{rel}:{no.lineno} importa {alias.name}. "
                                   f"Rota fala com service, não com modelo nem com o banco: mova a regra para {servico}.")
        elif isinstance(no, ast.ImportFrom) and no.module:
            nomes = {a.name for a in no.names}
            if no.module == "app.models" or no.module.startswith("app.models.") or (no.module == "app" and "models" in nomes):
                achados.append(f"{rel}:{no.lineno} importa {', '.join(sorted(nomes))} de {no.module}. "
                               f"Rota fala com service, não com modelo: mova a regra para {servico}.")
            elif no.module in PERMITIDO_NA_ROTA and not nomes <= PERMITIDO_NA_ROTA[no.module]:
                extras = nomes - PERMITIDO_NA_ROTA[no.module]
                achados.append(f"{rel}:{no.lineno} importa {', '.join(sorted(extras))} de {no.module}. "
                               f"A rota só usa {', '.join(sorted(PERMITIDO_NA_ROTA[no.module]))}; o resto fica em {servico}.")
        elif isinstance(no, ast.Call) and isinstance(no.func, ast.Attribute) and no.func.attr in ACESSO_AO_BANCO:
            # Qualquer objeto: o nome da variável da sessão não importa (db, banco, s...).
            dono = ast.unparse(no.func.value)
            achados.append(f"{rel}:{no.lineno} chama {dono}.{no.func.attr}() direto. "
                           f"Acesso ao banco fica no service: crie a função em {servico} e chame-a na rota.")
    return achados


def violacoes_do_servico(arquivo: Path) -> list[str]:
    rel = arquivo.relative_to(APP.parent.parent)
    achados = []
    for no in ast.walk(ast.parse(arquivo.read_text(encoding="utf-8"))):
        modulo = no.module if isinstance(no, ast.ImportFrom) else None
        nomes = [a.name for a in no.names] if isinstance(no, ast.Import) else []
        if (modulo and modulo.split(".")[0] == "fastapi") or any(n.split(".")[0] == "fastapi" for n in nomes):
            achados.append(f"{rel}:{no.lineno} importa o FastAPI. Service não conhece HTTP: levante NaoEncontrado "
                           f"ou RegraDeNegocio(detalhe, status=409) de app/services/erros.py; o main.py traduz.")
    return achados


def por_linha(achados: list[str]) -> list[str]:
    return sorted(achados, key=lambda a: int(a.split(":", 2)[1].split()[0]))


def verificar(excecoes: list[str]) -> list[str]:
    achados = []
    for arquivo in sorted((APP / "routes").glob("*.py")):
        if arquivo.name != "__init__.py" and f"routes/{arquivo.name}" not in excecoes:
            achados += por_linha(violacoes_da_rota(arquivo))
    for arquivo in sorted((APP / "services").glob("*.py")):
        if f"services/{arquivo.name}" not in excecoes:
            achados += por_linha(violacoes_do_servico(arquivo))
    return achados


def main():
    sensores = LAB / "sensores.toml"
    excecoes = tomllib.loads(sensores.read_text(encoding="utf-8"))["camadas"]["excecoes"] if sensores.exists() else ["routes/faturas.py"]
    achados = verificar(excecoes)
    for a in achados:
        print(f"camadas: {a}")
    print("camadas: PASS" if not achados else f"camadas: FAIL ({len(achados)} violações)")
    return 1 if achados else 0


if __name__ == "__main__":
    sys.exit(main())
