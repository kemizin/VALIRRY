import flet as ft
from datetime import date

from database.database import init_db, salvar_produto,listar_produtos


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

    lista_produtos = ft.Column(spacing=8)

    def carregar_produtos():
        lista_produtos.controls.clear()

        produtos_salvos = listar_produtos()

        if not produtos_salvos:
            lista_produtos.controls.append(
                ft.Text("Nenhum produto cadastrado ainda.")
            )
            return

        for item in produtos_salvos:
            (
                id_produto,
                codigo_barras_item,
                codigo_interno_item,
                produto_item,
                lote_item,
                validade_item,
                quantidade_item,
                data_conferencia_item
            ) = item

            lista_produtos.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                f"{produto_item}",
                                weight=ft.FontWeight.BOLD,
                                size=16
                            ),
                            ft.Text(f"Cód. interno: {codigo_interno_item}"),
                            ft.Text(f"Cód. barras: {codigo_barras_item}"),
                            ft.Text(f"Lote: {lote_item}"),
                            ft.Text(f"Validade: {validade_item}"),
                            ft.Text(f"Quantidade: {quantidade_item}"),
                            ft.Text(f"Conferido em: {data_conferencia_item}"),
                        ],
                        spacing=2
                    ),
                    padding=10,
                    bgcolor="#1E1E1E",
                    border_radius=8
                )
            )

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

        carregar_produtos()

        page.update()

    botao_salvar = ft.Button(
    content=ft.Text("Salvar"),
    on_click=salvar
    )
    

    carregar_produtos()

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
                ft.Text(
                    "Produtos cadastrados",
                    size=20,
                    weight=ft.FontWeight.BOLD
                ),
                lista_produtos,
            ],
            spacing=12,
            scroll=ft.ScrollMode.AUTO
        )
    )


ft.run(main)