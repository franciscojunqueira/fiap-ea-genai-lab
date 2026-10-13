

# RASCUNHO do colega (sexta à noite): cancelamento, ERP-142. Não terminei; fiz do jeito do faturas.py.
@router.post("/pedidos/{pedido_id}/cancelar", response_model=PedidoOut)
def cancelar_pedido(pedido_id: int, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    for item in pedido.itens:
        estoque = db.query(Estoque).filter(Estoque.produto_id == item.produto_id).first()
        estoque.quantidade += item.quantidade
    pedido.status = "CANCELADO"
    db.commit()
    return _pedido_to_out(pedido)
