import flet as ft
from datetime import date

from database.database import init_db, salvar_produto


def main(page: ft.Page):
    page.title = "VALIRRY"
    page.window.width = 500
    page.window.height = 700

    init_db()

    titulo = ft.Text(
        "VALIRRY",
        size=32,
        weight=ft.FontWeight.BOLD
    )

    subtitulo = ft.Text(
        "Controle de validade e lotes",
        size=16
    )

    codigo_barras = ft.TextField(
        label="Código de barras",
        autofocus=True
    )

    codigo_interno = ft.TextField(
        label="Código interno"
    )

    produto = ft.TextField(
        label="Nome do produto"
    )

    lote = ft.TextField(
        label="Lote"
    )

    validade = ft.TextField(
        label="Validade",
        hint_text="Ex: 20/07/2026"
    )

    quantidade = ft.TextField(
        label="Quantidade",
        keyboard_type=ft.KeyboardType.NUMBER
    )

    mensagem = ft.Text("")

    def salvar(e):
        if not produto.value or not lote.value or not validade.value or not quantidade.value:
            mensagem.value = "Preenche produto, lote, validade e quantidade."
            page.update()
            return

        try:
            quantidade_int = int(quantidade.value)
        except ValueError:
            mensagem.value = "Quantidade precisa ser um número."
            page.update()
            return

        salvar_produto(
            codigo_barras=codigo_barras.value,
            codigo_interno=codigo_interno.value,
            produto=produto.value,
            lote=lote.value,
            validade=validade.value,
            quantidade=quantidade_int,
            data_conferencia=str(date.today())
        )

        mensagem.value = "Produto salvo com sucesso!"

        codigo_barras.value = ""
        codigo_interno.value = ""
        produto.value = ""
        lote.value = ""
        validade.value = ""
        quantidade.value = ""

        page.update()

    botao_salvar = ft.Button(
    content=ft.Text("Salvar"),
    on_click=salvar
    )
    

    page.add(
        ft.Column(
            controls=[
                titulo,
                subtitulo,
                codigo_barras,
                codigo_interno,
                produto,
                lote,
                validade,
                quantidade,
                botao_salvar,
                mensagem,
            ],
            spacing=12
        )
    )


ft.run(main)