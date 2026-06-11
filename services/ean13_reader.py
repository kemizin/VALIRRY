import cv2
import numpy as np


#como a ideia é transformar em um app android fiz meu próprio leitor obs(não limpei isso ainda)



L_CODES = {
    "0001101": "0",
    "0011001": "1",
    "0010011": "2",
    "0111101": "3",
    "0100011": "4",
    "0110001": "5",
    "0101111": "6",
    "0111011": "7",
    "0110111": "8",
    "0001011": "9",
}

G_CODES = {
    "0100111": "0",
    "0110011": "1",
    "0011011": "2",
    "0100001": "3",
    "0011101": "4",
    "0111001": "5",
    "0000101": "6",
    "0010001": "7",
    "0001001": "8",
    "0010111": "9",
}

R_CODES = {
    "1110010": "0",
    "1100110": "1",
    "1101100": "2",
    "1000010": "3",
    "1011100": "4",
    "1001110": "5",
    "1010000": "6",
    "1000100": "7",
    "1001000": "8",
    "1110100": "9",
}

FIRST_DIGIT_PATTERNS = {
    "LLLLLL": "0",
    "LLGLGG": "1",
    "LLGGLG": "2",
    "LLGGGL": "3",
    "LGLLGG": "4",
    "LGGLLG": "5",
    "LGGGLL": "6",
    "LGLGLG": "7",
    "LGLGGL": "8",
    "LGGLGL": "9",
}


def validar_digito_ean13(codigo: str) -> bool:
    if len(codigo) != 13 or not codigo.isdigit():
        return False

    soma = 0

    for i, digito in enumerate(codigo[:12]):
        numero = int(digito)

        if i % 2 == 0:
            soma += numero
        else:
            soma += numero * 3

    digito_calculado = (10 - (soma % 10)) % 10

    return digito_calculado == int(codigo[-1])


def binarizar_imagem(caminho_imagem: str):
    imagem = cv2.imread(caminho_imagem)

    if imagem is None:
        raise FileNotFoundError(f"Imagem não encontrada: {caminho_imagem}")

    cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

    cinza = cv2.GaussianBlur(cinza, (3, 3), 0)

    _, binaria = cv2.threshold(
        cinza,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    return binaria

def salvar_debug_binaria(caminho_imagem: str, caminho_saida: str = "assets/debug_binaria.png"):
    binaria = binarizar_imagem(caminho_imagem)

    cv2.imwrite(caminho_saida, binaria)

    return caminho_saida

def linha_para_bits(linha):
    """
    Converte pixels em bits.
    Preto = 1
    Branco = 0
    """
    bits = []

    for pixel in linha:
        if pixel < 128:
            bits.append("1")
        else:
            bits.append("0")

    return "".join(bits)


def cortar_area_util(bits: str):
    """
    Remove branco sobrando antes/depois do código.
    """
    primeiro_preto = bits.find("1")
    ultimo_preto = bits.rfind("1")

    if primeiro_preto == -1 or ultimo_preto == -1:
        return None

    return bits[primeiro_preto:ultimo_preto + 1]


def normalizar_para_95_bits(bits: str):
    """
    EAN-13 tem 95 módulos:
    3 início + 42 esquerda + 5 meio + 42 direita + 3 fim
    """
    if len(bits) < 95:
        return None

    indices = np.linspace(0, len(bits) - 1, 95).astype(int)

    normalizado = "".join(bits[i] for i in indices)

    return normalizado


def decodificar_95_bits(bits: str):
    if len(bits) != 95:
        return None

    inicio = bits[0:3]
    meio = bits[45:50]
    fim = bits[92:95]

    if inicio != "101":
        return None

    if meio != "01010":
        return None

    if fim != "101":
        return None

    lado_esquerdo = bits[3:45]
    lado_direito = bits[50:92]

    digitos_esquerda = ""
    padrao_esquerda = ""

    for i in range(0, 42, 7):
        bloco = lado_esquerdo[i:i + 7]

        if bloco in L_CODES:
            digitos_esquerda += L_CODES[bloco]
            padrao_esquerda += "L"
        elif bloco in G_CODES:
            digitos_esquerda += G_CODES[bloco]
            padrao_esquerda += "G"
        else:
            return None

    if padrao_esquerda not in FIRST_DIGIT_PATTERNS:
        return None

    primeiro_digito = FIRST_DIGIT_PATTERNS[padrao_esquerda]

    digitos_direita = ""

    for i in range(0, 42, 7):
        bloco = lado_direito[i:i + 7]

        if bloco in R_CODES:
            digitos_direita += R_CODES[bloco]
        else:
            return None

    codigo = primeiro_digito + digitos_esquerda + digitos_direita

    if validar_digito_ean13(codigo):
        return codigo

    return None

def detectar_e_recortar_barcode(
    caminho_imagem: str,
    caminho_saida: str = "assets/debug_barcode_detectado.png"
):
    imagem = cv2.imread(caminho_imagem)

    if imagem is None:
        raise FileNotFoundError(f"Imagem não encontrada: {caminho_imagem}")

    original = imagem.copy()

    cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

    # Suaviza ruído
    cinza = cv2.GaussianBlur(cinza, (3, 3), 0)

    # Gradiente no eixo X encontra variações verticais típicas de barcode
    grad_x = cv2.Sobel(cinza, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
    grad_y = cv2.Sobel(cinza, ddepth=cv2.CV_32F, dx=0, dy=1, ksize=-1)

    gradiente = cv2.subtract(grad_x, grad_y)
    gradiente = cv2.convertScaleAbs(gradiente)

    # Borrão para unir as barras
    gradiente = cv2.blur(gradiente, (9, 9))

    # Binariza
    _, thresh = cv2.threshold(
        gradiente,
        225,
        255,
        cv2.THRESH_BINARY
    )

    # Fecha espaços entre barras
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 7))
    fechado = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Remove pequenos ruídos
    fechado = cv2.erode(fechado, None, iterations=4)
    fechado = cv2.dilate(fechado, None, iterations=4)

    contornos, _ = cv2.findContours(
        fechado,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contornos:
        return None

    # Pega o maior contorno
    maior_contorno = max(contornos, key=cv2.contourArea)

    x, y, w, h = cv2.boundingRect(maior_contorno)

# Código de barras é bem largo, então damos muita margem lateral
    margem_x = int(w * 4)
    margem_y = int(h * 2)

    # Margem mínima, caso o contorno detectado seja pequeno
    margem_x = max(margem_x, 150)
    margem_y = max(margem_y, 80)

    x1 = max(x - margem_x, 0)
    y1 = max(y - margem_y, 0)
    x2 = min(x + w + margem_x, original.shape[1])
    y2 = min(y + h + margem_y, original.shape[0])

    recorte = original[y1:y2, x1:x2]

    if recorte.size == 0:
        return None

    cv2.imwrite(caminho_saida, recorte)

    return caminho_saida

def tentar_ler_em_varias_versoes(caminho_imagem: str):
    imagem = cv2.imread(caminho_imagem)

    if imagem is None:
        raise FileNotFoundError(f"Imagem não encontrada: {caminho_imagem}")

    tentativas = []

    # Original
    tentativas.append(("original", imagem))

    # Aumenta resolução
    escala_2x = cv2.resize(
        imagem,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC
    )
    tentativas.append(("escala_2x", escala_2x))

    escala_3x = cv2.resize(
        imagem,
        None,
        fx=3,
        fy=3,
        interpolation=cv2.INTER_CUBIC
    )
    tentativas.append(("escala_3x", escala_3x))

    for nome, img in tentativas:
        caminho_temp = f"assets/debug_{nome}.png"
        cv2.imwrite(caminho_temp, img)

        codigo = ler_ean13_da_imagem(caminho_temp)

        if codigo:
            return codigo

    return None

def bits_para_runs(bits: str):
    """
    Transforma:
    111000110

    Em:
    [('1', 3), ('0', 3), ('1', 2), ('0', 1)]
    """
    if not bits:
        return []

    runs = []
    atual = bits[0]
    contador = 1

    for bit in bits[1:]:
        if bit == atual:
            contador += 1
        else:
            runs.append((atual, contador))
            atual = bit
            contador = 1

    runs.append((atual, contador))

    return runs


def juntar_runs_iguais(runs):
    if not runs:
        return []

    resultado = [runs[0]]

    for cor, largura in runs[1:]:
        ultima_cor, ultima_largura = resultado[-1]

        if cor == ultima_cor:
            resultado[-1] = (ultima_cor, ultima_largura + largura)
        else:
            resultado.append((cor, largura))

    return resultado


def limpar_runs_pequenos(runs):
    """
    Remove sujeirinhas pequenas causadas por blur/ruído.
    Exemplo: uma falha branca minúscula no meio de uma barra preta.
    """
    if not runs:
        return []

    total = sum(largura for _, largura in runs)
    modulo_estimado = total / 95

    limiar = max(1, int(modulo_estimado * 0.30))

    limpos = []

    for cor, largura in runs:
        if largura <= limiar and limpos:
            cor_anterior, largura_anterior = limpos[-1]
            limpos[-1] = (cor_anterior, largura_anterior + largura)
        else:
            limpos.append((cor, largura))

    return juntar_runs_iguais(limpos)


def runs_para_95_bits(runs):
    """
    Converte larguras reais de barras/espaços em 95 módulos EAN-13.
    """
    if not runs:
        return None

    total = sum(largura for _, largura in runs)

    if total < 95:
        return None

    modulo = total / 95

    bits = ""

    for cor, largura in runs:
        quantidade_modulos = int(round(largura / modulo))
        quantidade_modulos = max(1, quantidade_modulos)

        bits += cor * quantidade_modulos

    if len(bits) == 95:
        return bits

    return normalizar_para_95_bits(bits)


def decodificar_linha_por_largura(linha):
    bits = linha_para_bits(linha)

    bits = cortar_area_util(bits)

    if not bits:
        return None

    candidatos = []

    # tentativa com a linha inteira
    candidatos.append(bits)

    # tentativas cortando um pouco das bordas
    # isso ajuda quando pegou sujeira antes/depois do barcode
    margem_maxima = int(len(bits) * 0.08)
    margem_maxima = max(4, margem_maxima)

    passo = max(1, margem_maxima // 6)

    for corte_esquerda in range(0, margem_maxima + 1, passo):
        for corte_direita in range(0, margem_maxima + 1, passo):
            fim = len(bits) - corte_direita

            if fim <= corte_esquerda:
                continue

            candidato = bits[corte_esquerda:fim]

            if len(candidato) >= 95:
                candidatos.append(candidato)

    for candidato in candidatos:
        runs = bits_para_runs(candidato)

        for versao_runs in (runs, limpar_runs_pequenos(runs)):
            bits_95 = runs_para_95_bits(versao_runs)

            if not bits_95:
                continue

            codigo = decodificar_95_bits(bits_95)

            if codigo:
                return codigo

    return None



def ler_ean13_da_imagem(caminho_imagem: str):
    imagem = cv2.imread(caminho_imagem)

    if imagem is None:
        raise FileNotFoundError(f"Imagem não encontrada: {caminho_imagem}")

    cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

    binarizacoes = []

    # Otsu normal
    blur = cv2.GaussianBlur(cinza, (3, 3), 0)

    _, otsu = cv2.threshold(
        blur,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    binarizacoes.append(("otsu", otsu))

    # Adaptativo
    adaptativo = cv2.adaptiveThreshold(
        cinza,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        5
    )

    binarizacoes.append(("adaptativo", adaptativo))

    # Thresholds fixos
    for limite in [80, 100, 120, 140, 160, 180]:
        _, fixa = cv2.threshold(
            cinza,
            limite,
            255,
            cv2.THRESH_BINARY
        )

        binarizacoes.append((f"fixo_{limite}", fixa))

    for nome, binaria in binarizacoes:
        tentativas = [
            binaria,
            cv2.bitwise_not(binaria)
        ]

        for tentativa in tentativas:
            altura, largura = tentativa.shape

            # tenta várias linhas horizontais
            for percentual in range(20, 81, 2):
                y = int(altura * (percentual / 100))

                linha = tentativa[y, :]

                codigo = decodificar_linha_por_largura(linha)

                if codigo:
                    print(f"Leu usando: {nome} | linha {percentual}%")
                    return codigo

    return None

def gerar_versoes_processadas(caminho_imagem: str):
    imagem = cv2.imread(caminho_imagem)

    if imagem is None:
        raise FileNotFoundError(f"Imagem não encontrada: {caminho_imagem}")

    versoes = []

    escalas = [1, 2, 3]

    for escala in escalas:
        if escala == 1:
            img = imagem.copy()
        else:
            img = cv2.resize(
                imagem,
                None,
                fx=escala,
                fy=escala,
                interpolation=cv2.INTER_CUBIC
            )

        cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # versão normal
        versoes.append((f"escala_{escala}_cinza", cinza))

        # contraste
        contraste = cv2.equalizeHist(cinza)
        versoes.append((f"escala_{escala}_contraste", contraste))

        # blur leve
        blur = cv2.GaussianBlur(cinza, (3, 3), 0)
        versoes.append((f"escala_{escala}_blur", blur))

        # threshold otsu
        _, otsu = cv2.threshold(
            blur,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        versoes.append((f"escala_{escala}_otsu", otsu))

        # threshold adaptativo
        adaptativo = cv2.adaptiveThreshold(
            cinza,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            5
        )
        versoes.append((f"escala_{escala}_adaptativo", adaptativo))

        # sharpen
        kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ])

        sharpen = cv2.filter2D(cinza, -1, kernel)
        versoes.append((f"escala_{escala}_sharpen", sharpen))

    return versoes

def ler_ean13_com_tentativas(caminho_imagem: str):
    versoes = gerar_versoes_processadas(caminho_imagem)

    for nome, img in versoes:
        caminho_debug = f"assets/debug_tentativa_{nome}.png"
        cv2.imwrite(caminho_debug, img)

        # Se a imagem já estiver em grayscale/binary, precisamos salvar e reler
        codigo = ler_ean13_da_imagem(caminho_debug)

        if codigo:
            print(f"Leu na tentativa: {nome}")
            return codigo

        # tenta invertido também
        invertida = cv2.bitwise_not(img)
        caminho_invertido = f"assets/debug_tentativa_{nome}_invertida.png"
        cv2.imwrite(caminho_invertido, invertida)

        codigo = ler_ean13_da_imagem(caminho_invertido)

        if codigo:
            print(f"Leu na tentativa invertida: {nome}")
            return codigo

    return None

def ler_codigo_barras_da_imagem(caminho_imagem: str):
    recorte = detectar_e_recortar_barcode(caminho_imagem)

    if recorte:
        codigo = ler_ean13_da_imagem(recorte)

        if codigo:
            return codigo

        codigo = ler_ean13_com_tentativas(recorte)

        if codigo:
            return codigo

    codigo = ler_ean13_da_imagem(caminho_imagem)

    if codigo:
        return codigo

    codigo = ler_ean13_com_tentativas(caminho_imagem)

    if codigo:
        return codigo

    return None