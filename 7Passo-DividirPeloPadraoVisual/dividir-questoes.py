from PIL import Image
import os

def converter_cor_gimp_para_rgb(gimp_r, gimp_g, gimp_b):
    """
    Converte valores do GIMP (0-100) para RGB (0-255)
    """
    r = int((gimp_r / 100) * 255)
    g = int((gimp_g / 100) * 255)
    b = int((gimp_b / 100) * 255)
    return (r, g, b)

def encontrar_faixa_padrao(imagem, cor_alvo=(189, 188, 188), tolerancia=15, altura_alvo=64, margem_erro=4):
    """
    Encontra posições onde há uma faixa vertical da cor especificada com
    altura de 64 pixels (margem de erro de ±4 pixels: entre 60 e 68 pixels).
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    altura_min = altura_alvo - margem_erro  # 60 pixels
    altura_max = altura_alvo + margem_erro  # 68 pixels
    
    posicoes_corte = []
    
    y = 0
    while y < altura:
        # Conta a quantidade de pixels consecutivos da cor alvo no penúltimo pixel da largura (largura - 2)
        comprimento = 0
        while y + comprimento < altura:
            pixel = pixels[largura - 2, y + comprimento]
            
            if len(pixel) == 4:  # RGBA
                r, g, b, a = pixel
            else:  # RGB
                r, g, b = pixel[:3]
            
            # Verifica se a cor está dentro da tolerância
            if (abs(r - cor_alvo[0]) <= tolerancia and 
                abs(g - cor_alvo[1]) <= tolerancia and 
                abs(b - cor_alvo[2]) <= tolerancia):
                comprimento += 1
            else:
                break
        
        # Verifica se o comprimento da faixa encontrada está entre 60px e 68px
        if altura_min <= comprimento <= altura_max:
            posicao_corte = y  # Corta no início do padrão
            posicoes_corte.append(posicao_corte)
            print(f"Padrão de {comprimento}px encontrado em y={y}, cortando em y={posicao_corte}")
            y += comprimento  # Pula a faixa inteira para evitar re-detecção
        else:
            y += max(1, comprimento)
            
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo):
    """
    Divide a imagem verticalmente mantendo o padrão visual no início de cada corte
    """
    # Abre a imagem
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    # Encontra as posições do padrão
    posicoes_corte = encontrar_faixa_padrao(imagem, cor_alvo)
    
    if not posicoes_corte:
        print("Nenhum padrão encontrado na imagem!")
        return
    
    print(f"Encontradas {len(posicoes_corte)} faixas/padrões para corte")
    
    # Cria a pasta de saída se não existir
    os.makedirs(pasta_saida, exist_ok=True)
    
    # Corta as seções da imagem
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        # Garantir que a posição de corte é válida
        if posicao_corte <= posicao_anterior:
            continue
            
        # Corta a seção anterior
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        # Salva a imagem cortada
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        # A próxima seção começa EXATAMENTE no início do padrão visual encontrado,
        # garantindo que o padrão permaneça no topo/início da nova imagem.
        posicao_anterior = posicao_corte
    
    # Corta a seção final (do último padrão até o final da imagem)
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "./inteiras/pagina_enem_4.png"  # Substitua pelo caminho da sua imagem
    pasta_saida = "pg5"  # Substitua pelo nome da pasta de saída desejada

    # Cor RGB (0-255) informada: (189, 188, 188)
    cor_do_padrao = (189, 188, 188)
    print(f"Cor definida: RGB{cor_do_padrao}")
    
    # Executa a divisão
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_do_padrao)
    
    print("Divisão concluída!")