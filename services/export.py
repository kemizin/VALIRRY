from pathlib import Path
from datetime import date

import pandas as pd

from database.database import listar_produtos


EXPORTS_DIR = Path("exports")


def exportar_excel():
    EXPORTS_DIR.mkdir(exist_ok=True)

    produtos = listar_produtos()

    dados = []

    for item in produtos:
        (
            id_produto,
            codigo_barras,
            codigo_interno,
            produto,
            lote,
            validade,
            quantidade,
            data_conferencia
        ) = item

        dados.append({
            "ID": id_produto,
            "Código de Barras": codigo_barras,
            "Código Interno": codigo_interno,
            "Produto": produto,
            "Lote": lote,
            "Validade": validade,
            "Quantidade": quantidade,
            "Data Conferência": data_conferencia,
        })

    df = pd.DataFrame(dados)

    nome_arquivo = f"validades_{date.today()}.xlsx"
    caminho = EXPORTS_DIR / nome_arquivo

    df.to_excel(caminho, index=False)

    return caminho