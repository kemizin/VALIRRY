import sqlite3
from pathlib import Path

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

    cursor.execute("SELECT * FROM produtos")

    produtos = cursor.fetchall()

    conn.close()

    return produtos