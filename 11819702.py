# Melhoramento e Superresolução de Imagens
# Implementar métodos de melhoramento baseado em pixel

import imageio.v3 as imageio
import numpy as np
def histogram(A, n_niveis):
    # largura e altura da imagem
    N,M = A.shape
    # inicializa o histograma como zeros
    hist = np.zeros(n_niveis).astype(int)
    # loop pelas intensidades
    for i in range(n_niveis):
        # soma a quantidade de pixels com o mesmo valor de intensidade
        pixels = np.sum(A==i)
        # coloca a quantidade no histograma
        hist[i] = pixels
    return hist

def hist_equalization(A, n_niveis):
    # o primeiro elemento do histograma é o histograma comum dos niveis
    hist[0] = histogram(A, n_niveis)
    h_cumul = np.zeros(n_niveis).astype(int) #histograma cumulativo
    h_cumul[0] = hist[0]
    # o histograma cumulativo computa a soma dos niveis anteriores a cada nivel
    for i in range(1,n_niveis):
        h_cumul[i] = hist[i]+h_cumul[i-1]

    # histograma da funcao transformacao
    hist_transf = np.zeros(n_niveis).astype(np.uint8)

    # tamanho da imagem
    N,M = A.shape
    # criar a imagem para a armazenar a nova versão equalizada
    A_eq = np.zeros([N,M]).astype(np.uint8)

    # loop por cada nivel e transforme os valores z
    for z in range(n_niveis):
        # funcao transformacao dos niveis
        s = ((n_niveis-1)/float(M*N))*h_cumul[z]
        # coloca o nivel transformado no histograma novo
        hist_transf[z] = s

        # imagem equalizada: para cada coordenada em que A = z, substitua por s
        A_eq[np.where(A==z)] = s
    return A_eq

def hist_equalization_quatro(list_imgs,n_niveis):
    h_cumul = np.zeros(n_niveis).astype(int) #histograma cumulativo
    list_hist = []
    for img in list_imgs:
        # o primeiro elemento do histograma é o histograma comum dos niveis
        hist[0] = histogram(img, n_niveis)
        list_hist.append(hist[0])
    # soma todos os histogramas de cada imagem
    h_soma = sum(list_hist)
    # soma cumulativa dos niveis 
    for i in range(1,n_niveis):
        h_cumul[i] = h_soma[i]+h_cumul[i-1]

    # funcao transformacao
    hist_transf = np.zeros(n_niveis).astype(np.uint8)

    # tamanho da imagem
    N,M = list_imgs[0].shape
    final_img_list = []
    for img in list_imgs:
        img_eq = np.zeros(img.shape).astype(np.uint8)
        # função transformação para as quatro imagens juntas
        for z in range(n_niveis):
            s = ((n_niveis-1)/float(img.shape*4))*h_cumul[z]
            hist_transf[z] = s

            # para cada coordenada em que imagem = z, substitua por s
            img_eq[np.where(img==z)] = s
        # lista de imagens a serem retornadas
        final_img_list.append(img_eq)
    return final_img_list

def superresolution(hist_list):
    # a matriz final tem o dobro do tamanho das imagens low de entrada
    H_chapeu = np.zeros(hist_list[0].shape*2)
    count_imgs = 0
    n_linha = 0
    n_coluna = 0
    # largura e altura da primeira imagem da lista
    L,C = hist_list[0].shape
    # se for a imagem 0 ou 2
    for count_imgs in range(4):
        img = hist_list[count_imgs]
        for element in img:
            # preenche todas as colunas antes de passar a proxima linha
            while n_linha<=(L-1):
                if n_coluna<=(C-1):
                    H_chapeu[n_linha][n_coluna] = element
                    # cada elemento é inserido pulando uma coluna
                    n_coluna+=2
                # vai para a proxima linha daquela imagem
                n_linha+= 2
            count_imgs+=1
        # se for a imagem 0 ou 2, começa a inserir na primeira linha
        if count_imgs%2==0:
            n_linha = 0
            # a imagem 2 começa a inserir na segunda coluna
            if count_imgs == 2:
                n_coluna = 1
        # se for a imagem 1 ou 3, começa a inserir na segunda linha
        else:
            n_linha = 1
            # a imagem 1 começa a inserir na primeira coluna e a imagem 3 na segunda coluna
            if count_imgs == 1:
                n_coluna = 0
            else:
                n_coluna = 1
    return H_chapeu

def F_enhancement(img_list,id,gama):
    final_img_list = []
    
    # se é escolhida a opção zero, nenhum melhoramento é feito
    if id==0:
        final_img_list = img_list

    # se é escolhida a opção um, computa um histograma cumulativo para cada imagem e usa ele pra realizar equalização grayscale
    elif id==1:
        for img in img_list:
            # 256 niveis de gray scale
            img_eq = hist_equalization(img,256)
            final_img_list.append(img_eq)

    # se é escolhida a opção dois, computa um histograma cumulativo para todas as imagens e usa ele pra realizar equalização grayscale
    elif id==2:
        # teste com função nova
        final_img_list = hist_equalization_quatro(img_list,256)

    # se é opção 3: aplica uma função de correção gama
    elif id==3:
        gama_list = []
        for img in img_list:
            L_chapeu = []
            for element in img:
                L_chapeu.append(255*((img/255)**(1/gama)))
            gama_list.append(L_chapeu)
        final_img_list = gama_list
    return final_img_list


i = 0

img_base_name = input().rstrip()
import glob
procura = f"*{img_base_name}"
img_list = glob.glob(procura)


img_high = imageio.imread(input().rstrip())
F_choice = input().rstrip()
gama = input().rstrip()
final_img_list = F_enhancement(img_list,F_choice,gama)
H_chapeu = superresolution(final_img_list)
rmse = np.sqrt((np.array(img_high)-np.array(H_chapeu))**2/(img_high.shape*H_chapeu.shape))
print(rmse)