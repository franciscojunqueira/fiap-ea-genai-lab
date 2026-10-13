# -*- coding: utf-8 -*-
# acesso ao banco do SGC (sqlite desde 2019; antes era o Oracle compartilhado)
import os
import sqlite3

from sgc import config

ESQUEMA = """
CREATE TABLE IF NOT EXISTS sacado (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    nome_normalizado TEXT NOT NULL,
    documento TEXT NOT NULL,
    tipo TEXT NOT NULL,
    segmento TEXT DEFAULT 'VAREJO',
    telefone TEXT,
    saldo_devedor REAL DEFAULT 0,
    ultimo_pagamento TEXT
);

CREATE TABLE IF NOT EXISTS cobranca (
    id INTEGER PRIMARY KEY,
    nosso_numero TEXT UNIQUE,
    sacado_id INTEGER NOT NULL REFERENCES sacado(id),
    origem TEXT NOT NULL,
    origem_id TEXT,
    valor REAL NOT NULL,
    emissao TEXT NOT NULL,
    vencimento TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ABERTA',
    valor_pago REAL,
    data_pagamento TEXT,
    remessa TEXT
);

CREATE TABLE IF NOT EXISTS pagamento (
    id INTEGER PRIMARY KEY,
    cobranca_id INTEGER NOT NULL REFERENCES cobranca(id),
    valor REAL NOT NULL,
    data TEXT NOT NULL,
    ocorrencia TEXT NOT NULL,
    arquivo TEXT
);

CREATE TABLE IF NOT EXISTS pendente_agrupamento (
    id INTEGER PRIMARY KEY,
    sacado_id INTEGER NOT NULL REFERENCES sacado(id),
    origem TEXT NOT NULL,
    origem_id TEXT,
    valor REAL NOT NULL,
    criado_em TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS devolucao (
    id INTEGER PRIMARY KEY,
    cobranca_id INTEGER NOT NULL,
    valor REAL NOT NULL,
    criado_em TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS arquivo_processado (
    nome TEXT PRIMARY KEY,
    processado_em TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sequencia (
    nome TEXT PRIMARY KEY,
    valor INTEGER NOT NULL
);

-- saldo do sacado mantido por trigger (relatorio de risco le daqui)
CREATE TRIGGER IF NOT EXISTS trg_emissao AFTER INSERT ON cobranca
BEGIN
    UPDATE sacado SET saldo_devedor = saldo_devedor + NEW.valor WHERE id = NEW.sacado_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_pagamento AFTER INSERT ON pagamento
BEGIN
    UPDATE sacado
       SET saldo_devedor = saldo_devedor - NEW.valor,
           ultimo_pagamento = NEW.data
     WHERE id = (SELECT sacado_id FROM cobranca WHERE id = NEW.cobranca_id);
END;

-- pedido da Tesouraria (2018): pagamento de boleto ja baixado vira devolucao ao pagador
CREATE TRIGGER IF NOT EXISTS trg_pago_apos_baixa AFTER INSERT ON pagamento
WHEN (SELECT status FROM cobranca WHERE id = NEW.cobranca_id) = 'BAIXADA'
BEGIN
    INSERT INTO devolucao (cobranca_id, valor, criado_em) VALUES (NEW.cobranca_id, NEW.valor, NEW.data);
END;
"""


def conectar(caminho=None):
    caminho = caminho or config.DB_PATH
    pasta = os.path.dirname(caminho)
    if pasta and not os.path.isdir(pasta):
        os.makedirs(pasta)
    con = sqlite3.connect(caminho)
    con.row_factory = sqlite3.Row
    con.executescript(ESQUEMA)
    return con


def proximo_valor(con, nome):
    row = con.execute("SELECT valor FROM sequencia WHERE nome = ?", (nome,)).fetchone()
    if row is None:
        valor = 1
        con.execute("INSERT INTO sequencia (nome, valor) VALUES (?, ?)", (nome, valor))
    else:
        valor = row["valor"] + 1
        con.execute("UPDATE sequencia SET valor = ? WHERE nome = ?", (valor, nome))
    return valor
