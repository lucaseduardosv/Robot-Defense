import pygame
import sys
import os
# --------- Configurações ---------
largura = 1280         # largura da janela do jogo
altura = 720           # altura da janela do jogo
FPS = 60               # frames por segundo (velocidade do loop)

# Caminho da música (está uma pasta acima, dentro da pasta 'audio')
base_path = os.path.dirname(os.path.abspath(__file__))
caminho_musica = os.path.join(base_path, "som", "somdefundo.mp3")

# Cores usadas no jogo
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HIGHLIGHT = (255, 255, 0)  # amarelo para destacar os botões

# Inicializa todos os módulos do pygame (exceto mixer que será inicializado no menu)
pygame.init()

# Caminho do ícone (volta uma pasta e acessa teste.png)
icon_path = os.path.join(os.path.dirname(__file__),  "sprites", "Fundo.png")
icon = pygame.image.load(icon_path)
pygame.display.set_icon(icon)
pygame.display.set_caption("Robot Defense")

# Fonte usada nos botões ##### Procurar fonte ideal #####
FONT_BUTTON = pygame.font.SysFont("Poppins", 67)

# Cria a janela do jogo com o tamanho definido
tela = pygame.display.set_mode((largura, altura))

# Carrega a imagem de fundo do menu e ajusta para o tamanho da janela
caminho_fundo = os.path.join(os.path.dirname(__file__), "sprites", "Fundo.png")
fundo_original = pygame.image.load(caminho_fundo)
fundo = pygame.transform.scale(fundo_original, (largura, altura))


class Button:
    """Classe que representa um botão interativo no menu."""

    def __init__(self, text, pos, callback):
        self.text = text                  # texto exibido no botão
        self.callback = callback          # função chamada ao clicar no botão
        self.default_color = WHITE        # cor padrão do texto
        self.highlight_color = HIGHLIGHT  # cor quando mouse está em cima
        self.font = FONT_BUTTON           # fonte usada
        self.label = self.font.render(self.text, True, self.default_color)
        self.rect = self.label.get_rect(center=pos)  # retângulo para detectar clique e posição

    def draw(self, surface, mouse_pos):
        # Define cor do texto: destaca se mouse estiver sobre o botão
        if self.rect.collidepoint(mouse_pos):
            color = self.highlight_color
        else:
            color = self.default_color

        outline_color = BLACK  # cor da borda do texto para melhor leitura
        offsets = [(-1, -1), (-1, 0), (-1, 1),
                   (0, -1),           (0, 1),
                   (1, -1),  (1, 0),  (1, 1)]

        # Desenha a borda do texto com pequenos deslocamentos para criar efeito contorno
        for ox, oy in offsets:
            pos = self.rect.move(ox, oy)
            outline_surf = self.font.render(self.text, True, outline_color)
            surface.blit(outline_surf, pos)

        # Desenha o texto principal
        text_surf = self.font.render(self.text, True, color)
        surface.blit(text_surf, self.rect)

    def check_click(self, mouse_pos):
        # Se o clique aconteceu dentro do botão, executa a ação (callback)
        if self.rect.collidepoint(mouse_pos):
            self.callback()


class Menu:
    """Classe que gerencia o menu principal do jogo."""

    def __init__(self, screen):
        self.screen = screen
        mid_x = largura // 2      # posição horizontal central para os botões
        start_y = 380             # posição vertical inicial do primeiro botão
        gap = 60                  # espaçamento vertical entre os botões

        # Cria botões do menu com suas posições e funções
        self.buttons = [
            Button("play",    (mid_x, start_y), self.start_game),
            Button("options", (mid_x, start_y + gap), self.show_options),
            Button("quit",    (mid_x, start_y + 2 * gap), self.exit_game),
        ]

        self.running = True

        # Variáveis para animação do círculo de transição do menu
        self.animating_circle = True
        self.circle_radius = 0
        self.circle_center = (largura // 2, altura // 2)

        self.animation_done = False  # indica se animação terminou

    def start_game(self):
        print("Iniciando o jogo...")
        self.running = False  # fecha o menu para iniciar o jogo

    def show_options(self):
        print("Abrindo opções...")  # placeholder para futura tela de opções

    def exit_game(self):
        pygame.quit()
        sys.exit()  # encerra o programa

    def run(self):
        # Inicializa o mixer e toca a música do menu em loop infinito
        pygame.mixer.init()
        pygame.mixer.music.load(caminho_musica)
        pygame.mixer.music.set_volume(0.3)  # volume entre 0.0 e 1.0
        pygame.mixer.music.play(-1)         # -1 para tocar em loop

        clock = pygame.time.Clock()
        max_radius = int((largura ** 2 + altura ** 2) ** 0.5)  # diagonal da tela para animação

        while self.running:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game()

                # Só permite clicar nos botões após animação acabar
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.animation_done:
                    for btn in self.buttons:
                        btn.check_click(mouse_pos)

            # Desenha o fundo do menu
            self.screen.blit(fundo, (0, 0))

            # Animação do círculo que revela o menu
            if self.animating_circle:
                mask = pygame.Surface((largura, altura))
                mask.fill(BLACK)
                mask.set_colorkey((255, 0, 255))  # cor transparente da máscara
                pygame.draw.circle(mask, (255, 0, 255), self.circle_center, self.circle_radius)
                self.screen.blit(mask, (0, 0))

                self.circle_radius += 20  # aumenta o raio do círculo

                if self.circle_radius > max_radius:
                    self.animating_circle = False
                    self.animation_done = True

            # Após animação, desenha os botões e permite interação
            if self.animation_done:
                for btn in self.buttons:
                    btn.draw(self.screen, mouse_pos)

            pygame.display.flip()
            clock.tick(FPS)

        # Para a música quando o menu fechar
        pygame.mixer.music.stop()


class Game:
    """Classe principal do jogo."""

    def __init__(self):
        self.screen = pygame.display.set_mode((largura, altura))

    def run(self):
        # Executa o menu antes do jogo começar
        menu = Menu(self.screen)
        menu.run()
        self.game_loop()

    def game_loop(self):
       ''' clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Limpa a tela com cor cinza escura
            self.screen.fill((30, 30, 30))

            # Aqui vai o código do jogo propriamente dito

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()'''
       main()
       


if __name__ == "__main__":
    Game().run()