from pathlib import Path
from datetime import date

from openpyxl import Workbook

from database.database import listar_produtos


EXPORTS_DIR = Path("exports")


def exportar_excel():
    EXPORTS_DIR.mkdir(exist_ok=True)

    produtos = listar_produtos()

    nome_arquivo = f"validades_{date.today()}.xlsx"
    caminho = EXPORTS_DIR / nome_arquivo

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Validades"

    cabecalhos = [
        "ID",
        "Código de Barras",
        "Código Interno",
        "Produto",
        "Lote",
        "Validade",
        "Quantidade",
        "Data Conferência",
    ]

    sheet.append(cabecalhos)

    for item in produtos:
        sheet.append(list(item))

    workbook.save(caminho)

    return caminho