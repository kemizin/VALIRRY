from services.ean13_reader import (
    detectar_e_recortar_barcode,
    ler_ean13_da_imagem
)

imagem = "assets/sss.png"

recorte = detectar_e_recortar_barcode(imagem)

print("Recorte:", recorte)

if recorte:
    codigo = ler_ean13_da_imagem(recorte)
    print("Código:", codigo)
else:
    print("Nenhum barcode detectado.")