import pygame
from pygame.locals import *
from sys import exit
import os
from random import randrange, choice

pygame.init()
pygame.mixer.init()

diretorio_principal = os.path.dirname(__file__)
diretorio_imagens = os.path.join(diretorio_principal, 'imagens')
diretorio_sons = os.path.join(diretorio_principal, 'sons')

LARGURA = 640
ALTURA = 480

BRANCO = (255,255,255)

tela = pygame.display.set_mode((LARGURA, ALTURA))

pygame.display.set_caption('Dino Game')

# carregar som de colisão 
som_colisao = pygame.mixer.Sound(os.path.join(diretorio_sons, 'death_sound.wav'))
som_colisao.set_volume(1)

# carregar som de pontuação
som_pontuacao = pygame.mixer.Sound(os.path.join(diretorio_sons, 'score_sound.wav'))
som_pontuacao.set_volume(1)

# variavel controle para o som na colisão 
colidiu = False

# escolha do inimigo 
escolha_obstaculo = choice([0, 1])

pontos = 0
velocidade_jogo = 10

sprite_sheet = pygame.image.load(os.path.join(diretorio_imagens, 'dinoSpritesheet.png')).convert_alpha()

# função que cria mensagens formatadas prontas pra renderizar na tela
def exibe_mensagem(msg, tamanho, cor):
    fonte = pygame.font.SysFont('comicsansms', tamanho, True, False)
    mensagem = f'{msg}'
    texto_formatado = fonte.render(mensagem, True, cor)
    return texto_formatado

def reiniciar_jogo():
    global pontos, velocidade_jogo, colidiu, escolha_obstaculo
    pontos = 0
    velocidade_jogo = 10
    colidiu = False
    dino_voador.rect.x = LARGURA
    cacto.rect.x = LARGURA
    escolha_obstaculo = choice([0, 1])
    dino.rect.y = ALTURA - 64 - 96/2
    dino.pulo = False



class Dino(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.som_pulo = pygame.mixer.Sound(os.path.join(diretorio_sons, 'jump_sound.wav')) #carregar som do pulo
        self.som_pulo.set_volume(1) #alterar volume (0 a 1)
        self.imagens_dinossauro = []
        for i in range(3):
            img = sprite_sheet.subsurface((i*32,0), (32,32))
            img = pygame.transform.scale(img, (32*3, 32*3))
            self.imagens_dinossauro.append(img)
        
        self.index_lista = 0
        self.image = self.imagens_dinossauro[self.index_lista]
        self.rect = self.image.get_rect()

        # mascara que serve de base pra detectar a colisão (todos os objetos que tem colisão devem ter esse parametro)
        self.mask = pygame.mask.from_surface(self.image)

        self.pos_y_inicial = ALTURA - 64 - 96/2  # -96/2 corrigir a posição, que no rect.center usa o ponto central do frame, enquanto no rect.y usa o ponto superior esquerdo (reposicionar no chão usando o ponto superior esquerdo)
        self.rect.center = (100, ALTURA - 64)
        self.pulo = False

    def pular(self):
        self.pulo = True
        self.som_pulo.play()

    def update(self):
        if self.pulo: 
            self.rect.y -= 15
            if self.rect.y <= 250: 
                self.pulo = False
        else: 
            if self.rect.y < self.pos_y_inicial: 
                self.rect.y += 15

        if self.index_lista > 2:
            self.index_lista = 0
        self.index_lista += 0.25
        self.image = self.imagens_dinossauro[int(self.index_lista)]


class Nuvens (pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = sprite_sheet.subsurface((7*32, 0), (32, 32)) #(x inicial, y inicial) (x final, y final)
        self.image = pygame.transform.scale(self.image, (32*3, 32*3)) # aumenta a imagem em 3x 
        self.rect = self.image.get_rect() 
        self.rect.center = (100, 100)
        self.rect.y = randrange(50, 200, 50)
        self.rect.x = LARGURA - randrange(50, 500, 100)
        self.velocidade = 10

    def update(self): 
        if self.rect.topright[0] < 0: # retorna um (x, y) do topo direito do quadrado da imagem
            self.rect.x = LARGURA
            self.rect.y = randrange(50, 200, 50)

            
        self.rect.x -= velocidade_jogo

class Chao(pygame.sprite.Sprite):
    def __init__(self, pos_x):
        pygame.sprite.Sprite.__init__(self)
        self.image = sprite_sheet.subsurface((6*32, 0), (32, 32)) #(x inicial, y inicial) (quanto anda pra frente (x) na imagem, quanto em y)
        self.image = pygame.transform.scale(self.image, (32*2, 32*2)) # aumenta a imagem em 3x 
        self.rect = self.image.get_rect() 
        self.rect.y = ALTURA - 64
        self.rect.x = pos_x*64

    def update(self):
        if self.rect.topright[0] < 0:
            self.rect.x = LARGURA
        self.rect.x -= 10

class Cacto(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = sprite_sheet.subsurface((5*32, 0), (32, 32))
        self.image = pygame.transform.scale(self.image, (32*2, 32*2)) # aumenta a imagem em 3x 
        self.rect = self.image.get_rect() 

        # mascara pra detectar colisão
        self.mask = pygame.mask.from_surface(self.image)

        # variavel de controle para definir se obstaculo aparece ou não na tela (cacto ou dino voador)
        self.escolha = escolha_obstaculo

        self.rect.center = (LARGURA, ALTURA - 64)
        
        # pra o cacto começar fora da tela, caso não seja sorteado primeiro 
        self.rect.x = LARGURA

    def update(self):
        if self.escolha == 0: 
            if self.rect.topright[0] < 0: 
                self.rect.x = LARGURA
            self.rect.x -= velocidade_jogo

class DinoVoador(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        #extração das imagens da sprite
        self.imagens_dinossauro = [] 
        for i in range(3, 5): 
            img = sprite_sheet.subsurface((i*32, 0), (32, 32))
            img = pygame.transform.scale(img, (32*3, 32*3))
            self.imagens_dinossauro.append(img)

        #carregar primeira imagem 
        self.index_lista = 0
        self.image = self.imagens_dinossauro[self.index_lista]

        # mascara para detectar colisões
        self.mask = pygame.mask.from_surface(self.image)
        
        # variavel de controle para definir se obstaculo aparece ou não na tela (cacto ou dino voador)
        self.escolha = escolha_obstaculo

        # ajustando posição inicial do dino na tela
        self.rect = self.image.get_rect() 
        self.rect.center = (LARGURA, 300)

        # pra o dino começar fora da tela, caso não seja sorteado primeiro 
        self.rect.x = LARGURA

    def update(self):
        if self.escolha == 1:
            # fazer andar na tela 
            if self.rect.topright[0] < 0:
                self.rect.x = LARGURA
            self.rect.x -= velocidade_jogo

            # animar sprite
            if self.index_lista > 1:
                self.index_lista = 0
            self.index_lista += 0.20
            self.image = self.imagens_dinossauro[int(self.index_lista)]

 
todas_as_sprites = pygame.sprite.Group()
dino = Dino()
todas_as_sprites.add(dino)

for i in range(4):
    nuvem = Nuvens() 
    todas_as_sprites.add(nuvem)

for i in range(LARGURA*2//64): # *2 pra resolver um bug das posições do chão 
    chao = Chao(i)
    todas_as_sprites.add(chao)

cacto = Cacto() 
todas_as_sprites.add(cacto)

dino_voador = DinoVoador() 
todas_as_sprites.add(dino_voador)

grupo_obstaculos = pygame.sprite.Group()
grupo_obstaculos.add(cacto)
grupo_obstaculos.add(dino_voador)


relogio = pygame.time.Clock()
while True:
    relogio.tick(30)
    tela.fill(BRANCO)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        if event.type == KEYDOWN: 
            if event.key == K_SPACE and not colidiu: 
                if dino.rect.y != dino.pos_y_inicial:
                    pass
                else:
                    dino.pular() 
            
            # restart - apenas se o jogo acabou
            if event.key == K_r and colidiu: 
                reiniciar_jogo() 

    # detectar colisoes da sprite principal (dino) com o grupo de obstaculos 
        # pygame.sprite.collide_mask - define o tipo de colisão, neste caso a verificação é pixel a pixel 
    colisoes = pygame.sprite.spritecollide(dino, grupo_obstaculos, False, pygame.sprite.collide_mask)

    todas_as_sprites.draw(tela)

    # para de atualizar a tela (pausa o game) quando colide
    if colisoes and not colidiu: 
        som_colisao.play() 
        colidiu = True

    if colidiu: 
        if pontos % 100 == 0: pontos += 1
        
        # mensagem game over
        game_over = exibe_mensagem('GAME OVER', 40, (0, 0, 0))
        tela.blit(game_over, (LARGURA // 2, ALTURA // 2))

        restart = exibe_mensagem('pressione r para reiniciar', 20, (0, 0, 0))
        tela.blit(restart, (LARGURA // 2, ALTURA // 2 + 60))

    # se o dino não colidiu com nada (continua o jogo)
    else: 
        pontos += 1
        todas_as_sprites.update()
        texto_pontos = exibe_mensagem(pontos, 40, (0, 0, 0))

    # som de pontuação (a cada 100 pontos) e aumento de velocidade
    if pontos % 100 == 0:
        som_pontuacao.play()
        if velocidade_jogo <= 23: velocidade_jogo += 1

    #renderiza texto dos pontos na tela
    tela.blit(texto_pontos, (520, 30))

    # refazer sorteio do proximo obstaculo 
    if cacto.rect.topright[0] <= 0 or dino_voador.rect.topright[0] <= 0:
        escolha_obstaculo = choice([0, 1])

        # voltar os obstaculos pra posição inicial
        cacto.rect.x = LARGURA
        dino_voador.rect.x = LARGURA

        # atualizar o valor sorteado nos objetos de obstaculo
        dino_voador.escolha = escolha_obstaculo
        cacto.escolha = escolha_obstaculo

    pygame.display.flip()