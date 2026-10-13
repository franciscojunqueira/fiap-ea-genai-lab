import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.db import engine, SessionLocal, Base
from app.models import Produto, Estoque, Pedido, ItemPedido, Fatura  # noqa: F401
from app.seed import seed_db
from app.routes import produtos, estoque, pedidos, faturas, alertas

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
