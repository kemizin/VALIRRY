import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("database/estoque.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_barras TEXT,
        codigo_interno TEXT,
        produto TEXT,
        lote TEXT,
        validade TEXT,
        quantidade INTEGER,
        data_conferencia TEXT
    )
    """)

    conn.commit()
    conn.close()

def salvar_produto(
    codigo_barras,
    codigo_interno,
    produto,
    lote,
    validade,
    quantidade,
    data_conferencia
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO produtos (
            codigo_barras,
            codigo_interno,
            produto,
            lote,
            validade,
            quantidade,
            data_conferencia
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        codigo_barras,
        codigo_interno,
        produto,
        lote,
        validade,
        quantidade,
        data_conferencia
    ))

    conn.commit()
    conn.close()

def listar_produtos():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            codigo_barras, 
            codigo_interno,
            produto,
            lote,
            validade,
            quantidade,
            data_conferencia
        FROM produtos
        ORDER BY id DESC
    """)

    produtos = cursor.fetchall()

    conn.close()

    return produtos

def atualizar_produto(
    id_produto,
    codigo_barras,
    codigo_interno,
    produto,
    lote,
    validade,
    quantidade,
    data_conferencia
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE produtos
        SET
            codigo_barras = ?,
            codigo_interno = ?,
            produto = ?,
            lote = ?,
            validade = ?,
            quantidade = ?,
            data_conferencia = ?
        WHERE id = ?
    """, (
        codigo_barras,
        codigo_interno,
        produto,
        lote,
        validade,
        quantidade,
        data_conferencia,
        id_produto
    ))

    conn.commit()
    conn.close()

def deletar_produto(id_produto):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM produtos
        WHERE id = ?
    """, (id_produto,))

    conn.commit()
    conn.close()

def listar_produtos_ate_validade(data_limite):
    produtos = listar_produtos()
    produtos_filtrados = []

    limite = datetime.strptime(data_limite, "%d/%m/%Y")

    for item in produtos:
        validade_item = item[5]

        try:
            validade_convertida = datetime.strptime(validade_item, "%d/%m/%Y")
        except ValueError:
            continue

        if validade_convertida <= limite:
            produtos_filtrados.append(item)

    return produtos_filtrados