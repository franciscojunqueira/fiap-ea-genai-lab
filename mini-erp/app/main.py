import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from app.db import engine, SessionLocal, Base
from app.models import Produto, Estoque, Pedido, ItemPedido, Fatura  # noqa: F401
from app.seed import seed_db
from app.routes import produtos, estoque, pedidos, faturas, alertas
from app.services.erros import NaoEncontrado, RegraDeNegocio

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Criar tabelas e popular dados iniciais
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_db(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Mini-ERP Didático",
    description="API de distribuição/vendas para laboratório de aula",
    version="1.0.0",
    lifespan=lifespan,
)

# Os services levantam erros de negócio; aqui eles viram HTTP, no mesmo formato {"detail": ...} do FastAPI.
@app.exception_handler(NaoEncontrado)
def tratar_nao_encontrado(request: Request, erro: NaoEncontrado):
    return JSONResponse(status_code=404, content={"detail": str(erro)})


@app.exception_handler(RegraDeNegocio)
def tratar_regra_de_negocio(request: Request, erro: RegraDeNegocio):
    return JSONResponse(status_code=erro.status, content={"detail": str(erro)})


app.include_router(produtos.router)
app.include_router(estoque.router)
app.include_router(pedidos.router)
app.include_router(faturas.router)
app.include_router(alertas.router)


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "mini-erp"}
