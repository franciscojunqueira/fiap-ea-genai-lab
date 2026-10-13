from sqlalchemy.orm import Session
from app.models import Produto, Estoque

PRODUTOS_INICIAIS = [
    {"nome": "Notebook Básico",    "descricao": "Notebook para uso corporativo",  "preco": 2500.00, "ativo": True},
    {"nome": "Mouse USB",          "descricao": "Mouse óptico com fio",           "preco": 50.00,   "ativo": True},
    {"nome": "Teclado Mecânico",   "descricao": "Teclado mecânico compacto",      "preco": 350.00,  "ativo": True},
    {"nome": "Monitor 24pol",      "descricao": "Monitor LED Full HD 24 pol",     "preco": 1200.00, "ativo": True},
    {"nome": "Webcam HD",          "descricao": "Webcam 1080p com microfone",     "preco": 200.00,  "ativo": False},
]

ESTOQUES_INICIAIS = [10, 100, 30, 15, 50]


def seed_db(db: Session):
    """Popula o banco com dados iniciais se estiver vazio."""
    if db.query(Produto).first():
        return  # já tem dados

    for i, dados in enumerate(PRODUTOS_INICIAIS):
        produto = Produto(**dados)
        db.add(produto)
        db.flush()  # gera o id

        estoque = Estoque(produto_id=produto.id, quantidade=ESTOQUES_INICIAIS[i])
        db.add(estoque)

    db.commit()
