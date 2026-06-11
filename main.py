import flet as ft
from datetime import date

from database.database import (
    init_db,
    salvar_produto,
    listar_produtos,
    atualizar_produto,
    deletar_produto,
    listar_produtos_ate_validade
)

from services.export import exportar_excel

from services.date_utils import formatar_validade

from services.ean13_reader import ler_codigo_barras_da_imagem


def main(page: ft.Page):
    page.title = "VALIRRY"
    page.window.width = 500
    page.window.height = 700
    page.scroll = ft.ScrollMode.AUTO
    conteudo = ft.Column()


    init_db()

#=================================
#exibição em abas 
#+++++++++++++++++++++++++++++++++

    def mostrar_cadastro():
        conteudo.controls.clear()

        conteudo.controls.append(
            ft.Column(
                controls=[
                    ft.Text("Cadastro", size=24, weight=ft.FontWeight.BOLD),
                    codigo_barras,
                    botao_ler_codigo_imagem,
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

        page.update()


    def mostrar_produtos():
        carregar_produtos()

        conteudo.controls.clear()

        conteudo.controls.append(
            ft.Column(
                controls=[
                    ft.Text("Produtos cadastrados", size=24, weight=ft.FontWeight.BOLD),
                    lista_produtos,
                ],
                spacing=12
            )
        )

        page.update()

#=========================
#barcode
#++++++++++++++++++++++++
    async def selecionar_imagem_codigo(e):
        arquivos = await ft.FilePicker().pick_files(
            allow_multiple=False,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["png", "jpg", "jpeg"]
        )

        if not arquivos:
            mensagem.value = "Nenhuma imagem selecionada."
            page.update()
            return

        caminho_imagem = arquivos[0].path

        if not caminho_imagem:
            mensagem.value = "Não consegui acessar o caminho da imagem."
            page.update()
            return

        codigo = ler_codigo_barras_da_imagem(caminho_imagem)

        if codigo:
            codigo_barras.value = codigo
            mensagem.value = f"Código lido: {codigo}"
        else:
            mensagem.value = "Não consegui ler o código nessa imagem."

        page.update()


    botao_ler_codigo_imagem = ft.Button(
        content="Ler código por imagem",
        on_click=selecionar_imagem_codigo
    )



#======================================
#relatorio de validades
#++++++++++++++++++++++++++++++++++++++
    data_limite_relatorio = ft.TextField(
        label="Mostrar produtos que vencem até",
        hint_text="Ex: 30/11/2026"
    )

    resultado_relatorio = ft.Column(spacing=8)

    def gerar_relatorio(e):
        resultado_relatorio.controls.clear()

        try:
            data_formatada = formatar_validade(data_limite_relatorio.value)
        except ValueError:
            mensagem.value = "Data limite inválida. Use algo tipo 30/11/2026 ou 301126."
            page.update()
            return

        produtos_filtrados = listar_produtos_ate_validade(data_formatada)

        if not produtos_filtrados:
            resultado_relatorio.controls.append(
                ft.Text("Nenhum produto encontrado nesse período.")
            )
            page.update()
            return

        for item in produtos_filtrados:
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

            resultado_relatorio.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(f"{produto_item}", weight=ft.FontWeight.BOLD, size=16),
                            ft.Text(f"Cód. interno: {codigo_interno_item}"),
                            ft.Text(f"Lote: {lote_item}"),
                            ft.Text(f"Validade: {validade_item}"),
                            ft.Text(f"Quantidade: {quantidade_item}"),
                        ],
                        spacing=2
                    ),
                    padding=10,
                    bgcolor="#1E1E1E",
                    border_radius=8
                )
            )

        mensagem.value = f"Relatório gerado até {data_formatada}."
        page.update()
    def mostrar_relatorios():
        conteudo.controls.clear()

        conteudo.controls.append(
            ft.Column(
                controls=[
                    ft.Text("Relatórios", size=24, weight=ft.FontWeight.BOLD),
                    data_limite_relatorio,
                    ft.Button(
                        content="Gerar relatório",
                        on_click=gerar_relatorio
                    ),
                    resultado_relatorio,
                    mensagem,
                ],
                spacing=12
            )
        )

        page.update()
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

                        ft.Row(
                            controls=[
                                ft.Button(
                                    content="Editar",
                                    on_click=lambda e, item=item: carregar_para_edicao(item)
                                ),
                                ft.Button(
                                    content="Excluir",
                                    on_click=lambda e, id_produto=id_produto: deletar_item(id_produto)
                                ),
                            ],
                            spacing=10
                        )
                    ],
                    spacing=4
                ),
                padding=10,
                bgcolor="#1E1E1E",
                border_radius=8
            )

            lista_produtos.controls.append(card)

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
            validade_formatada = formatar_validade(validade.value)
        except ValueError:
            mensagem.value = "Validade inválida. Use algo tipo 20/07/2026 ou 200726."
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
                validade=validade_formatada,
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
                validade=validade_formatada,
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

#============================
#apagar
#++++++++++++++++++++++++++++

    def deletar_item(id_produto):
        deletar_produto(id_produto)

        mensagem.value = "Produto deletado com sucesso!"

        limpar_campos()
        carregar_produtos()
        page.update()



#=============================
#page adds 
#++++++++++++++++++++++++++++
    barra_abas = ft.Row(
        controls=[
            ft.Button(
                content="Cadastro",
                on_click=lambda e: mostrar_cadastro()
            ),
            ft.Button(
                content="Produtos",
                on_click=lambda e: mostrar_produtos()
            ),
            botao_exportar,
            ft.Button(
                content="Relatórios",
                on_click=lambda e: mostrar_relatorios()
            ),
        ],
        spacing=13,
        scroll=ft.ScrollMode.AUTO
    )

    page.add(
        ft.Column(
            controls=[
                ft.Text("VALIRRY", size=32, weight=ft.FontWeight.BOLD),

                barra_abas,

                conteudo,
            ],
            spacing=13
        )
    )

    mostrar_cadastro()


ft.run(main)

