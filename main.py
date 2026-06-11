import flet as ft
from datetime import date

from database.database import (
    init_db,
    salvar_produto,
    listar_produtos,
    atualizar_produto
)
from services.export import exportar_excel

def main(page: ft.Page):
    page.title = "VALIRRY"
    page.window.width = 500
    page.window.height = 700
    page.scroll = ft.ScrollMode.AUTO


    init_db()
#======================================
#dicionario pra não brigar com nonlocal
#++++++++++++++++++++++++++++++++++++++

    produto_em_edicao = {"id": None}

#+++++++++++++++++++++++++++++++++++++++
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
#========================
#CARREGAR produtos
#++++++++++++++++++++++++ 
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

            card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(f"{produto_item}", weight=ft.FontWeight.BOLD, size=16),
                    ft.Text(f"Cód. interno: {codigo_interno_item}"),
                    ft.Text(f"Cód. barras: {codigo_barras_item}"),
                    ft.Text(f"Lote: {lote_item}"),
                    ft.Text(f"Validade: {validade_item}"),
                    ft.Text(f"Quantidade: {quantidade_item}"),
                    ft.Text(f"Conferido em: {data_conferencia_item}"),
                    ft.Text("Clique para editar", size=12),
                ],
                spacing=2
            ),
            padding=10,
            bgcolor="#1E1E1E",
            border_radius=8
        )

        lista_produtos.controls.append(
            ft.GestureDetector(
                content=card,
                on_tap=lambda e, item=item: carregar_para_edicao(item)
            )
        )

#==========================
#limpar campos
#+++++++++++++++++++++++++

    def limpar_campos():
        produto_em_edicao["id"] = None

        codigo_barras.value = ""
        codigo_interno.value = ""
        produto.value = ""
        lote.value = ""
        validade.value = ""
        quantidade.value = ""

        botao_salvar.content = "Salvar"
    def carregar_para_edicao(item):
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

        produto_em_edicao["id"] = id_produto

        codigo_barras.value = codigo_barras_item
        codigo_interno.value = codigo_interno_item
        produto.value = produto_item
        lote.value = lote_item
        validade.value = validade_item
        quantidade.value = str(quantidade_item)

        botao_salvar.content = "Atualizar"
        mensagem.value = f"Editando: {produto_item} | Lote {lote_item}"

        page.update()

#==========================
#SALVAR
#+++++++++++++++++++++++++


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

        if produto_em_edicao["id"] is None:
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

        else:
            atualizar_produto(
                id_produto=produto_em_edicao["id"],
                codigo_barras=codigo_barras.value,
                codigo_interno=codigo_interno.value,
                produto=produto.value,
                lote=lote.value,
                validade=validade.value,
                quantidade=quantidade_int,
                data_conferencia=str(date.today())
            )

            mensagem.value = "Produto atualizado com sucesso!"

        limpar_campos()
        carregar_produtos()
        page.update()

    botao_salvar = ft.Button(
    content=ft.Text("Salvar"),
    on_click=salvar
    )

#==============================
#EXPORTAR
#+++++++++++++++++++++++++++++
    def exportar(e):
        caminho = exportar_excel()
        mensagem.value = f"Excel exportado: {caminho}"
        page.update()

    carregar_produtos()

    botao_exportar = ft.Button(
        content="Exportar Excel",
        on_click=exportar
    )

#=============================
#page adds 
#++++++++++++++++++++++++++++
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
                botao_exportar,
                mensagem,
                ft.Text(
                    "Produtos cadastrados",
                    size=20,
                    weight=ft.FontWeight.BOLD
                ),
                lista_produtos,
            ],
            spacing=12,
        )
    )


ft.run(main)