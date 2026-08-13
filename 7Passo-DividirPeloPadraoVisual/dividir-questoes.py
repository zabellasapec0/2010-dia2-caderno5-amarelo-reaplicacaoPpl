"""
Propósito: Dividir as questões por padrão. Observa-se que ao início de cada questão tem uma faixa de alguma cor, que é o padrão de início de cada questão
Autor: Alexandre Nassar de Peder
Criação: 02/10/2025
Atualização: 03/06/2026

OBS1: puxe a imagem "colunas_concatenadas_verticalmente.png" do passo 6 para essa pasta do passo 7

OBS2: puxe a pasta "inteiras" do passo 5 para essa pasta do passo 7

OBS3: este código foi originalmente preparado para percorrer cada pixel de cima para baixo, analizando o penúltimo pixel da direita (linha 55), procurando por um padrão visual vertical de 10 pixels RGB 0-255 (64, 193, 243), seguido de 7 pixels RGB 0-255 (179, 230, 250), 4 px RGB 0-255 (64, 193, 243) e 8 px RGB 0-255 (179, 230, 250). Quando encontrava esse padrão, cortava-se 13 pixels acima de começar o padrão (linha 71).

OBS4: tendo isso em mente, use o GIMP para identificar qual é o padrão visual da sua prova (que indica o início de cada questão), quantos pixels acima do padrão visual você precisa cortar, e também qual pixel é melhor percorrer para procurar por essa faixa. SEJA CRÍTICO(A)!

OBS5: em algumas situações, o pixel procurado é a mesma cor de uma imagem ou letra. Nesses casos, você pode pedir para percorrer uma faixa de determinada altura e largura e determinada cor, e não apenas um pixel. Isso vai depender do padrão visual da sua prova.

OBS6: além disso, em algumas situações, o padrão visual varia um pixel ou outro. Por isso, é interessante considerar uma margem de erro de 3 pixels para mais e 3 pixels para menos em cada uma das faixas do seu padrão visual.

OBS6: use IA para mudar minimamente o código a fim de cortar sua imagem seguindo o padrão visual vertical da sua prova, qual pixel percorrer, qual cor RGB 0-255 procurar, quantos pixels acima do padrão visual cortar, e se necessário, percorrer uma faixa de determinada altura e largura e determinada cor, e não apenas um pixel.

OBS7: rode esse código para cada imagem que você precisa cortar. Atualize as linhas 138 e 139 para identificar a imagem e atualize o nome da pasta de saída também

OBS8: execute o código, e abra as imagens para conferir se as questões foram divididas corretamente. Se não, ajuste os valores de corte e execute novamente.
"""

"""
Propósito: Dividir as questões por padrão visual (faixa cinza vertical/horizontal no canto direito).
Autor: Alexandre Nassar de Peder
Atualizado para buscar faixa cinza RGB (73,74) de 28px de altura (margem ±3px)
e realizar o corte 8px acima do início do padrão.
"""

"""
Propósito: Dividir as questões por padrão visual (faixa cinza).
Atualizado com suporte a imagens grandes, tolerância ajustada e logs de diagnóstico.
"""
"""
Propósito: Dividir as questões por padrão visual (faixa cinza).
Ajuste: Adicionada varredura horizontal para ignorar a borda preta e localizar
a faixa cinza mesmo que ela esteja deslocada para o interior da imagem.
"""

"""
Propósito: Dividir as questões por padrão visual (faixa cinza).
Versão otimizada para imagens da pasta 'inteiras' com margens brancas largas.
"""

import os
from PIL import Image

# Desativa limite de pixels para imagens grandes
Image.MAX_IMAGE_PIXELS = None


def cor_corresponde(pixel, cor_alvo, tolerancia=25):
    """Verifica se um pixel RGB ou RGBA corresponde à cor alvo."""
    if len(pixel) == 4:
        r, g, b, _ = pixel
    else:
        r, g, b = pixel[:3]

    return (
        abs(r - cor_alvo[0]) <= tolerancia
        and abs(g - cor_alvo[1]) <= tolerancia
        and abs(b - cor_alvo[2]) <= tolerancia
    )


def encontrar_coluna_faixa(
    imagem, cor_alvo, tolerancia=25, profundidade_busca=200
):
    """Varre da borda direita para dentro em toda a extensão da imagem para

    encontrar a coluna X onde a faixa cinza se localiza.
    """
    largura, altura = imagem.size
    pixels = imagem.load()

    contagem_x = {}

    print(
        f"[Info] Mapeando colunas nos últimos {profundidade_busca}px da direita ao longo de toda a imagem..."
    )

    # Amostragem vertical ao longo de toda a altura (passos de 20px)
    for x in range(largura - 1, max(0, largura - profundidade_busca), -2):
        contagem_x[x] = 0
        for y in range(0, altura, 20):
            if cor_corresponde(pixels[x, y], cor_alvo, tolerancia):
                contagem_x[x] += 1

    melhor_x = max(contagem_x, key=contagem_x.get)

    if contagem_x[melhor_x] > 0:
        distancia = largura - 1 - melhor_x
        print(
            f"[Sucesso] Faixa cinza identificada na coluna X = {melhor_x} (distância da borda direita: {distancia}px)"
        )
        return melhor_x

    return None


def encontrar_faixa_cinza(
    imagem,
    coluna_x,
    cor_alvo=(73, 73, 74),
    tolerancia=25,
    altura_base=28,
    margem_erro=3,
    deslocamento_corte=8,
):
    """Percorre a imagem verticalmente na coluna X e recorta 8px acima da faixa."""
    largura, altura = imagem.size
    pixels = imagem.load()

    posicoes_corte = []
    altura_minima = altura_base - margem_erro  # 25px
    altura_maxima = altura_base + margem_erro  # 31px

    y = 0
    while y < altura - altura_minima:
        altura_encontrada = 0

        for dy in range(altura_maxima):
            if (y + dy) >= altura:
                break

            pixel_alvo = pixels[coluna_x, y + dy]

            if cor_corresponde(pixel_alvo, cor_alvo, tolerancia):
                altura_encontrada += 1
            else:
                break

        # Valida a faixa encontrada na faixa de 25px a 31px
        if altura_minima <= altura_encontrada <= altura_maxima:
            posicao_corte = max(0, y - deslocamento_corte)
            posicoes_corte.append((posicao_corte, altura_encontrada))
            print(
                f"Faixa cinza de {altura_encontrada}px detectada em y={y}. Cortando em y={posicao_corte}"
            )
            y += altura_encontrada
        else:
            y += 1

    return posicoes_corte


def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo=(73, 73, 74)):
    """Divide a imagem verticalmente salvando na pasta de saída."""
    os.makedirs(pasta_saida, exist_ok=True)

    if not os.path.exists(caminho_imagem):
        print(f"Erro: O arquivo '{caminho_imagem}' não foi encontrado!")
        return

    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size

    print(f"Imagem carregada: {largura}x{altura} pixels")

    # 1. Busca a coluna X correta
    coluna_x = encontrar_coluna_faixa(
        imagem, cor_alvo, tolerancia=25, profundidade_busca=200
    )

    if coluna_x is None:
        print(
            "\n[Aviso] Nenhuma faixa com a cor RGB informada foi encontrada nos últimos 200px da direita."
        )
        print(
            "Verifique se o tom de cinza do padrão nesta imagem inteira difere de RGB(73, 73, 74)."
        )
        return

    # 2. Localiza as faixas verticalmente
    resultados_faixas = encontrar_faixa_cinza(
        imagem, coluna_x=coluna_x, cor_alvo=cor_alvo, tolerancia=25
    )

    if not resultados_faixas:
        print(
            "\n[Aviso] Coluna identificada, mas nenhuma faixa atendeu ao critério de altura (28px ± 3px)."
        )
        return

    print(f"\nEncontradas {len(resultados_faixas)} faixas cinzas para corte.")

    # 3. Processa e salva as partes recortadas
    posicao_anterior = 0

    for i, (posicao_corte, altura_faixa) in enumerate(resultados_faixas):
        if posicao_corte <= posicao_anterior:
            continue

        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)

        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

        posicao_anterior = posicao_corte + 8 + altura_faixa

    # Bloco final da imagem
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)

        nome_arquivo = f"parte_{len(resultados_faixas)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")


if __name__ == "__main__":
    # Ajuste o nome da imagem e da pasta de saída conforme o OBS7
    caminho_imagem = (
        "inteiras_concatenadas_verticalmente.png"  # ex: "imagem_inteira.png"
    )
    pasta_saida = "inteiras_divididas"

    cor_do_padrao = (73, 73, 74)

    dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_do_padrao)
    print("\nProcesso finalizado!")