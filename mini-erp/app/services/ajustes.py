"""Ajuste de estoque em três passos: solicitar (agente) → aprovar (pessoa, pela tela) → executar (uma vez).

A regra fica aqui, no sistema de registro, e não no agente: sem aprovação, executar é recusado; executar
de novo devolve o mesmo resultado sem mexer no estoque (idempotência pela chave do ajuste).
"""
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Produto
from app.models_ajustes import AjusteEstoque
from app.services import estoque as estoque_service
from app.services.erros import NaoEncontrado, RegraDeNegocio


def solicitar(db: Session, produto_id: int, variacao: int, motivo: str, solicitante: str) -> AjusteEstoque:
    if not db.get(Produto, produto_id):
        raise NaoEncontrado("Produto não encontrado")
    if variacao == 0:
        raise RegraDeNegocio("A variação não pode ser zero: use +N para entrada e -N para saída")
    if not motivo.strip():
        raise RegraDeNegocio("Informe o motivo do ajuste")
    estoque_service.consultar(db, produto_id)
    ajuste = AjusteEstoque(produto_id=produto_id, variacao=variacao, motivo=motivo.strip(),
                           solicitado_por=solicitante.strip() or "não informado")
    db.add(ajuste)
    db.commit()
    db.refresh(ajuste)
    return ajuste


def obter(db: Session, ajuste_id: int) -> AjusteEstoque:
    ajuste = db.get(AjusteEstoque, ajuste_id)
    if not ajuste:
        raise NaoEncontrado("Ajuste não encontrado")
    return ajuste


def listar(db: Session, limit: int = 50) -> list[AjusteEstoque]:
    return db.query(AjusteEstoque).order_by(AjusteEstoque.id.desc()).limit(limit).all()


def decidir(db: Session, ajuste_id: int, aprovador: str, aprovar: bool) -> AjusteEstoque:
    ajuste = obter(db, ajuste_id)
    if ajuste.status != "PENDENTE":
        raise RegraDeNegocio(f"Ajuste já está {ajuste.status}", status=409)
    if not aprovador.strip():
        raise RegraDeNegocio("Informe o nome de quem aprova")
    if aprovador.strip().lower() == ajuste.solicitado_por.lower():
        raise RegraDeNegocio("Quem pediu o ajuste não pode aprová-lo", status=409)
    ajuste.status = "APROVADO" if aprovar else "REJEITADO"
    ajuste.aprovado_por = aprovador.strip()
    ajuste.decidido_em = datetime.now()
    db.commit()
    db.refresh(ajuste)
    return ajuste


def executar(db: Session, ajuste_id: int) -> AjusteEstoque:
    ajuste = obter(db, ajuste_id)
    if ajuste.status == "EXECUTADO":
        return ajuste
    if ajuste.status != "APROVADO":
        raise RegraDeNegocio(f"Ajuste {ajuste.id} está {ajuste.status}: só executa depois que uma pessoa aprovar "
                             "na tela do ERP (aba Aprovações)", status=409)
    estoque = estoque_service.consultar(db, ajuste.produto_id)
    if estoque.quantidade + ajuste.variacao < 0:
        raise RegraDeNegocio(f"O estoque ficaria negativo ({estoque.quantidade} {ajuste.variacao:+d})", status=409)
    ajuste.estoque_antes = estoque.quantidade
    estoque.quantidade += ajuste.variacao
    ajuste.estoque_depois = estoque.quantidade
    ajuste.status = "EXECUTADO"
    ajuste.executado_em = datetime.now()
    db.commit()
    db.refresh(ajuste)
    return ajuste
