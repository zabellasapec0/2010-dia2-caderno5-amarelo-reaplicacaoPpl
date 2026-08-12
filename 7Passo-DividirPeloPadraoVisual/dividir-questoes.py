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

from PIL import Image
import os

# Desativa o limite de tamanho de imagem do Pillow para arquivos gigantes
Image.MAX_IMAGE_PIXELS = None 

def cor_corresponde(pixel, cor_alvo, tolerancia=25):
    """
    Verifica se a cor do pixel está dentro da tolerância do RGB alvo.
    """
    if len(pixel) == 4:  # RGBA
        r, g, b, a = pixel
        if a < 128:  # Ignora pixels transparentes
            return False
    else:  # RGB
        r, g, b = pixel[:3]
        
    return (abs(r - cor_alvo[0]) <= tolerancia and 
            abs(g - cor_alvo[1]) <= tolerancia and 
            abs(b - cor_alvo[2]) <= tolerancia)

def encontrar_faixa_cinza(imagem, cor_alvo, tolerancia=25, altura_min=44, altura_max=56, offset_corte=8, margem_direita=15):
    """
    Busca faixas cinzas varrendo as colunas no canto direito da imagem,
    sendo tolerante a pequenos ruídos/pixels fora do padrão.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    # Define quais colunas testar na direita (da borda para dentro)
    colunas_x = [largura - 1 - i for i in range(margem_direita) if (largura - 1 - i) >= 0]
    
    y = 0
    while y < altura - altura_min:
        faixa_encontrada = False
        altura_faixa_detectada = 0

        for x in colunas_x:
            contagem_pixels = 0
            
            # Percorre a altura máxima da faixa para contar pixels correspondentes
            for dy in range(altura_max):
                if y + dy >= altura:
                    break
                
                pixel = pixels[x, y + dy]
                if cor_corresponde(pixel, cor_alvo, tolerancia):
                    contagem_pixels += 1
                else:
                    # Permite até 3 pixels "sujos" na faixa antes de quebrar a contagem
                    if dy > 5 and contagem_pixels < dy - 3:
                        break
            
            # Se encontrou uma quantidade válida de pixels da cor dentro do intervalo esperado
            if altura_min <= contagem_pixels <= altura_max:
                faixa_encontrada = True
                altura_faixa_detectada = contagem_pixels
                break
        
        if faixa_encontrada:
            posicao_corte = y - offset_corte
            if posicao_corte < 0:
                posicao_corte = 0
                
            posicoes_corte.append((posicao_corte, y, altura_faixa_detectada))
            print(f"-> Faixa encontrada em y={y} (altura de ~{altura_faixa_detectada}px), cortando em y={posicao_corte}")
            
            # Avança após o final da faixa encontrada
            y += altura_faixa_detectada
        else:
            y += 1
    
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo):
    """
    Divide a imagem verticalmente mantendo o padrão no topo de cada parte.
    """
    if not os.path.exists(caminho_imagem):
        print(f"ERRO: O arquivo '{caminho_imagem}' não foi encontrado na pasta!")
        return

    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    # Executa a busca com tolerância ampliada (25) e varredura nos últimos 15px da direita
    dados_corte = encontrar_faixa_cinza(
        imagem, 
        cor_alvo, 
        tolerancia=25,       # Aumentada para aceitar pequenas variações de tom
        altura_min=44,       # Margem levemente expandida (50 - 6px)
        altura_max=56,       # Margem levemente expandida (50 + 6px)
        offset_corte=8, 
        margem_direita=15    # Procura nos últimos 15 pixels da direita
    )
    
    if not dados_corte:
        print("\nNenhuma faixa cinza foi encontrada!")
        print("Dica: Verifique no GIMP o RGB exato da faixa nessa imagem específica.")
        return
    
    print(f"\nEncontradas {len(dados_corte)} faixas cinzas para corte.")
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, (posicao_corte, y_faixa_inicio, altura_faixa) in enumerate(dados_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        posicao_anterior = posicao_corte

    # Salva o bloco final após o último corte
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(dados_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    # Garanta que o nome do arquivo corresponda exatamente ao arquivo da pasta
    caminho_imagem = "colunas_concatenadas_verticalmente.png" 
    pasta_saida = "colunas"

    cor_do_padrao = (73, 73, 74)
    print(f"Cor alvo configurada: RGB{cor_do_padrao}")
    
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_do_padrao)
    print("Processo finalizado!")