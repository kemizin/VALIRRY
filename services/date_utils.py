from datetime import datetime


def formatar_validade(valor: str) -> str:
    valor = valor.strip()

    formatos = [
        "%d/%m/%Y",
        "%d/%m/%y",
        "%d-%m-%Y",
        "%d-%m-%y",
        "%d%m%Y",
        "%d%m%y",
    ]

    for formato in formatos:
        try:
            data = datetime.strptime(valor, formato)
            return data.strftime("%d/%m/%Y")
        except ValueError:
            pass

    raise ValueError("Data inválida")