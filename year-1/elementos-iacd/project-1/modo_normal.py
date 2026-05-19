# Importações necessárias
import tkinter as tk  # Importa o módulo tkinter para a criação da interface gráfica
import random  # Importa o módulo random para gerar números aleatórios
from tkinter import messagebox  # Importa a classe messagebox do módulo tkinter para exibir mensagens de caixa de diálogo
from collections import deque  # Importa a classe deque do módulo collections para criar uma fila
from PIL import ImageTk, Image, ImageFilter  # Importa as classes necessárias do módulo Pillow para trabalhar com imagens
from tabuleiros import maze_dificil, maze_facil, maze_medio  # Importa os tabuleiros de labirinto de outro arquivo chamado tabuleiros.py

# Funções para a janela inicial do jogo
def iniciar_jogo():
    messagebox.showinfo("Instruções", "Bem-vindo ao jogo! Escolhe um dos três níveis de dificuldades para começares...")

def mostrar_regras():
    regras_window = tk.Toplevel()  # Cria uma nova janela para exibir as regras
    regras_window.title("Regras do Jogo")  # Define o título da janela de regras
    regras_label = tk.Label(regras_window, text="Regras do Jogo:\n\n\n1. Use as setas do teclado ou as setas W A S D do teclado para mover o jogador.\n2. Evite os obstáculos (blocos pretos) e alcance a saída (bloco vermelho).\n3. Complete o tabuleiro, sabendo que:\n- Tem de passar por todos os blocos brancos exatamente uma vez;\n- O caminho deve alternar entre segmentos horizontais e verticais e dois segmentos consecutivos não podem ter o mesmo comprimento.", font=("Arial", 12, "bold"), fg='black')  # Cria um rótulo para exibir as regras do jogo
    regras_label.pack(padx=100, pady=200)  # Empacota o rótulo na janela de regras com preenchimento

def iniciar_jogo_apos_instrucoes():
    janela_inicial.destroy()  # Destroi a janela inicial após o jogador clicar no botão "Iniciar Jogo"
    iniciar_jogo()  # Chama a função para iniciar o jogo

def set_background_image(janela):
    # Carregue a imagem de fundo
    image = Image.open("\\Users\Leonor Carvalho\Desktop\capa_2.png") #Abre a imagem de fundo do arquivo 
    image = image.resize((janela.winfo_screenwidth(), janela.winfo_screenheight()))  # Redimensiona a imagem para o tamanho da tela
 
    photo = ImageTk.PhotoImage(image) # Cria um objeto ImageTk com a imagem redimensionada

    # Crie um Label para exibir a imagem como fundo
    background_label = tk.Label(janela, image=photo)
    background_label.image = photo  # Mantem uma referência à imagem para evitar a coleta de lixo

    # Defina a posição do Label para ocupar toda a janela
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Criação da janela inicial
janela_inicial = tk.Tk()  # Cria uma instância da classe Tk para a janela inicial do jogo
janela_inicial.title("Labirinto - Menu Inicial")  # Define o título da janela inicial
janela_inicial.configure(bg='black')  # Configura o fundo da janela inicial para preto

# Chama a função para definir a imagem de fundo
set_background_image(janela_inicial)

# Defina as dimensões da janela para ocupar todo o ecrã
largura_ecra = janela_inicial.winfo_screenwidth()
altura_ecra = janela_inicial.winfo_screenheight()
janela_inicial.geometry(f"{largura_ecra}x{altura_ecra}+0+0") # Define as dimensões e a posição da janela inicial

texto_instrucoes = "Bem-vindo ao Unequal Length Mazes!\n\nTrabalho Realizado por:\n- Ana Matilde Ferreira\n- Maria Leonor Carvalho\n\n Cadeira:\nElementos de Inteligência Artificial e Ciência de Dados"
# Cria uma caixa de texto sem preenchimento de fundo e sem realce
lbl_instrucoes = tk.Label(janela_inicial, text=texto_instrucoes, padx=300, pady=0, font=("Arial", 13, "bold"), bg='black', fg='white')
lbl_instrucoes.config(bg=janela_inicial.cget('bg'))  # Define a cor de fundo para corresponder à cor de fundo da janela
lbl_instrucoes.place(relx=0.5, rely=0.35, anchor="center")

# Cria os botões "Iniciar Jogo" e "Regras"
btn_iniciar = tk.Button(janela_inicial, text="Iniciar Jogo", command=iniciar_jogo_apos_instrucoes, bg='white', fg='black', font=("Arial", 15))
btn_iniciar.place(relx=0.5, rely=0.55, anchor="center")

btn_regras = tk.Button(janela_inicial, text="Regras", command=mostrar_regras, bg='white', fg='black', font=("Arial", 15))
btn_regras.place(relx=0.5, rely=0.65, anchor="center")

# Inicia o loop principal do tkinter para exibir a janela inicial
janela_inicial.mainloop()

class GridGUI:
    def __init__(self, master, grid):
        # Inicializa a classe com o mestre da interface gráfica e a grade do labirinto
        self.master = master
        self.master = master
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.block_size = 50 # Tamanho dos blocos na interface gráfica
        self.colors = {0: "white", 1: "black", 2: "red", 3: "green", 4: "blue", 5: "yellow"}
        self.player_color = "blue"  # Cor do jogador
        self.player_size = 40  # Tamanho do jogador
        self.player_position = (len(grid)-1, 0)
        self.visited = set() # Conjunto para armazenar as células visitadas
        self.canvas = tk.Canvas(master, width=self.cols * self.block_size, height=self.rows * self.block_size) # Criação do canvas
        self.canvas.pack()  # Coloca o canvas na interface gráfica
        self.btn_resolver = tk.Button(master, text="Resolver", command=self.resolver_tabuleiro, bg='black', fg='white', font=("Arial", 15))
        self.btn_resolver.pack(pady=10)
        self.btn_tentar_novamente = tk.Button(master, text="Tentar Novamente", command=self.reset_game, bg='black', fg='white', font=("Arial", 15))
        self.btn_tentar_novamente.pack(pady=10)
        self.previous_position = {}  # Dicionário vazio para armazenar as posições anteriores do jogador
        self.direcao_anterior = None  # Direção anterior do jogador
        self.direcao_agora = None  # Direção atual do jogador
        self.count_celulas_agora = 1
        self.count_celulas_anterior = 0
        self.draw_grid()  # Desenha a grade do labirinto
        self.draw_player()  # Desenha o jogador na posição inicial
        self.previous_position = None  # Inicialize previous_position como None

        self.master.bind("<KeyPress>", self.move_player) # Associa a função move_player à pressão de teclas


    def draw_grid(self):
         # Desenha a grade do labirinto no canvas
        for row in range(self.rows):
            for col in range(self.cols):
                x0 = col * self.block_size
                y0 = row * self.block_size
                x1 = x0 + self.block_size
                y1 = y0 + self.block_size

                # Mapeia os valores numéricos para as cores correspondentes
                color = self.colors[self.grid[row][col]]
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="black")

    def draw_player(self):
        # Desenha o jogador na posição inicial no canvas
        row, col = self.player_position
        x0 = col * self.block_size + (self.block_size - self.player_size) // 2  # Centraliza o jogador horizontalmente
        y0 = row * self.block_size + (self.block_size - self.player_size) // 2  # Centraliza o jogador verticalmente
        x1 = x0 + self.player_size
        y1 = y0 + self.player_size
        self.player = self.canvas.create_oval(x0, y0, x1, y1, fill=self.player_color) # Desenha o jogador como um círculo no canvas

    def check_game_state(self):
       # Verifica o estado do jogo para determinar se o jogador venceu, perdeu ou pode continuar a jogar.
        if self.player_position == (0, self.cols - 1):
            # Marca a célula de saída como vermelha
            self.grid[0][self.cols - 1] = 2

            # Verifica se todas as células do tabuleiro foram visitadas
            if len(self.visited) == (self.rows * self.cols) - sum(row.count(1) for row in self.grid):
                messagebox.showinfo("Vitória!", "Parabéns! Terminaste o tabuleiro.")
                self.master.quit() #Fecha o jogo
                return True
            else:
                # Se o jogador não visitou todas a células
                # Mensagem de derrota com dois botões
                result = messagebox.askquestion("Derrota", "Não passaste por todas as células! Game Over.\nQueres tentar novamente?")
                if result == 'yes':  # Se o jogador escolher tentar novamente
                    self.reset_game()
                else:  # Se o jogador escolher fechar o jogo
                    self.master.quit()
                return True

        # Verifica se o jogador está encurralado
        row, col = self.player_position
        valid_indices = [(row-1, col), (row+1, col), (row, col-1), (row, col+1)]
        valid_cells = [(r, c) for r, c in valid_indices if 0 <= r < self.rows and 0 <= c < self.cols]

        # Verifica se há movimentos possíveis ao redor do jogador
        for r, c in valid_cells:
            if self.grid[r][c] == 0 or self.grid[r][c] == 2:
                return False  # Existe pelo menos uma célula branca ou de saída ao redor do jogador

        # Se não houver movimentos possíveis ao redor do jogador, ele está encurralado
        result = messagebox.askquestion("Derrota", "Estás encurralado! Game Over.\nQueres tentar novamente?")
        if result == 'yes':  # Se o jogador escolher tentar novamente
            self.reset_game()
        else:  # Se o jogador escolher fechar o jogo
            self.master.quit()

        # Marca a célula de saída como vermelha
        self.grid[0][self.cols - 1] = 2
        return True

    def move_player(self, event):
        # Move o jogador na direção correspondente à tecla pressionada
        key = event.keysym
        row, col = self.player_position
        new_row, new_col = row, col  # Definindo inicialmente as novas posições como as atuais

        if key == "Up" or key == "w":
            self.direcao_agora = "vertical"
            new_row = row - 1
        elif key == "Down" or key == "s":
            self.direcao_agora = "vertical"
            new_row = row + 1
        elif key == "Left" or key == "a":
            self.direcao_agora = "horizontal"
            new_col = col - 1
        elif key == "Right" or key == "d":
            self.direcao_agora = "horizontal"
            new_col = col + 1

        # Verifica se o movimento é válido antes de atualizar a posição do jogador
        if 0 <= new_row < self.rows and 0 <= new_col < self.cols and self.grid[new_row][new_col] != 1 and (new_row, new_col) not in self.visited:
            # Marca a posição inicial como visitada automaticamente após o jogador sair dela pela primeira vez
            if self.player_position == (self.rows - 1, 0):
                self.visited.add(self.player_position)
            # Verifica se o jogador não está a tentar voltar para a posição inicial
            if self.player_position != (self.rows - 1, 0) or (new_row, new_col) != (0, self.cols - 1):
                # Atualiza a posição do jogador
                self.player_position = (new_row, new_col)
                # Desenha uma linha do jogador anterior para o novo jogador
                self.canvas.create_line(col * self.block_size + self.block_size // 2,
                                        row * self.block_size + self.block_size // 2,
                                        new_col * self.block_size + self.block_size // 2,
                                        new_row * self.block_size + self.block_size // 2,
                                        fill="blue", width=5)
                # Move o jogador na interface
                self.canvas.move(self.player, (new_col - col) * self.block_size, (new_row - row) * self.block_size)
                # Adiciona a posição atual às posições visitadas
                self.visited.add(self.player_position)
                # Pinta a célula visitada de amarelo, exceto se for a entrada
                if self.grid[new_row][new_col] != 3:  # Se não for a entrada (verde)
                    self.grid[new_row][new_col] = 5
                    x0 = new_col * self.block_size
                    y0 = new_row * self.block_size
                    x1 = x0 + self.block_size
                    y1 = y0 + self.block_size
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill="yellow", outline="black")
                # Verifica o estado do jogo após o movimento
                if self.check_game_state():
                    return

        #Se é a primeira jogada
        if self.direcao_anterior == None:
            self.direcao_anterior = self.direcao_agora
            
        else:
            if self.direcao_anterior == self.direcao_agora:
                self.count_celulas_agora += 1
            else:
                if self.count_celulas_agora == self.count_celulas_anterior:
                    # Se o número de movimentos na jogada atual for igual ao da jogada anterior
                    # Mensagem de derrota com dois botões
                    result = messagebox.askquestion("Derrota", "A jogada anterior teve o mesmo número de movimentos que a jogada atual! Game Over.\nQueres tentar novamente?")
                    if result == 'yes':  # Se o jogador escolher tentar novamente
                        self.reset_game()
                    else:  # Se o jogador escolher fechar o jogo
                        self.master.quit()
                    self.direcao_anterior = None
                    self.direcao_agora = None
                    self.count_celulas_agora = 1
                    self.count_celulas_anterior = 0
                    return True
                else:
                    self.count_celulas_anterior = self.count_celulas_agora
                    self.count_celulas_agora = 1
                    self.direcao_anterior = self.direcao_agora

    def reset_game(self):
        # Reiniciar todos os atributos relevantes para recomeçar o jogo
        self.visited = set()  # Limpa o conjunto de células visitadas
        self.longest_path = []  # Limpa o caminho mais longo encontrado
        self.longest_path_length = 0  # Reseta o comprimento do caminho mais longo

        # Limpar as células pintadas de amarelo
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == 5:# Se a célula estiver pintada de amarelo
                    self.grid[row][col] = 0  # Restaura para a cor branca
                    x0 = col * self.block_size
                    y0 = row * self.block_size
                    x1 = x0 + self.block_size
                    y1 = y0 + self.block_size
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill="white", outline="black")

        # Redesenhar o jogador na posição inicial
        self.player_position = (len(self.grid) - 1, 0)
        self.draw_player()

        # Garantir que a célula de saída seja vermelha
        self.grid[0][self.cols - 1] = 2

    def resolver_tabuleiro(self):
        # Resolver o tabuleiro encontrando o maior caminho
        self.reset_game() # Redefine o jogo
        def is_valid(row, col):
            return 0 <= row < self.rows and 0 <= col < self.cols and self.grid[row][col] != 1

        def get_valid_neighbors(row, col):
            valid_neighbors = []
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_row, new_col = row + dr, col + dc
                if is_valid(new_row, new_col) and (new_row, new_col) not in self.visited:
                    valid_neighbors.append((new_row, new_col))
            return valid_neighbors

        def get_valida_repeat():
            vtemp_path = []
            for indice in range(len(self.longest_path)):
                elista = True
                for vitem in range(len(self.longest_path[indice])):
                    if self.longest_path[indice].count(self.longest_path[indice][vitem]) > 1:
                        elista = False
                        break
                if elista:
                    vtemp_path.append(self.longest_path[indice])
            self.longest_path = vtemp_path

        def get_valida_trocos():
            vtemp_path = []

            retira = 0
            for ll in range(self.rows):
                for cc in range(self.cols):
                    if self.grid[ll][cc] == 1:
                        retira += 1
            contador = self.cols * self.rows - retira

            for path in self.longest_path:
                vrow_old, vcol_old = path[0]
                vrow, vcol = path[0]
                vcur_troco_len = 1
                vant_troco_len = 0
                vdirecao_ant = None
                vdirecao_agora = None
                vpathvalida = True
                for p in path[1:]:
                    vrow, vcol = p
                    if vcol_old != vcol:
                        vdirecao_agora = "horizontal"
                    elif vrow_old != vrow:
                        vdirecao_agora = "vertical"

                    if vdirecao_ant == None:
                        vdirecao_ant = vdirecao_agora
                        vcur_troco_len += 1
                    else:
                        if (vdirecao_ant == vdirecao_agora):
                            vcur_troco_len += 1
                        else:
                            if vcur_troco_len == vant_troco_len:
                                # Sai sinalizando que não é percurso válido
                                vpathvalida = False
                                break
                            else:
                                vant_troco_len = vcur_troco_len
                                vcur_troco_len = 2
                                vdirecao_ant = vdirecao_agora
                    

                    vrow_old, vcol_old = p

                if vpathvalida:
                    if len(path) == contador:
                        vtemp_path.append(path)

            if len(vtemp_path) >= 1:
                self.longest_path = list(vtemp_path[0])    

        def dfs(current_row, current_col, path_length, path):

            if (current_row, current_col) == (0, self.cols - 1):

                if path_length >= self.longest_path_length:
                    if path_length > self.longest_path_length:
                        self.longest_path_length = []    
                    #Valida que troços consecutivos não têm o mesmo tamanho
                    self.longest_path_length = path_length
                    self.longest_path.append(list(path))
                return
            
            for neighbor_row, neighbor_col in get_valid_neighbors(current_row, current_col):
                path.append((neighbor_row, neighbor_col))
                self.visited.add((neighbor_row, neighbor_col))
                dfs(neighbor_row, neighbor_col, path_length + 1, path)
                path.pop()
                self.visited.remove((neighbor_row, neighbor_col))

        # Inicializa as variáveis para a busca em profundidade (Depth-First Search)
        self.longest_path = []  # Armazena o caminho mais longo encontrado
        self.longest_path_length = 0  # Armazena o comprimento do caminho mais longo encontrado
        start_row, start_col = self.rows - 1, 0  # Posição inicial do jogador
        dfs(start_row, start_col, 1, [(start_row, start_col)])  # Inicia a busca em profundidade com a posição inicial
        get_valida_repeat()
        get_valida_trocos()

        # Desenha o caminho mais longo encontrado
        if self.longest_path:
            start_position = (start_row, start_col)
            end_position = (0, self.cols - 1)
            self.draw_solution(start_position, end_position, self.longest_path) # Desenha o caminho
            # Após encontrar a solução, redefina o jogo para permitir que o jogador tente novamente
            self.reset_game()


    def update_gui(self, current_row, current_col):
        # Atualiza a interface gráfica com a posição atual do jogador
        x = current_col * self.block_size + self.block_size // 2
        y = current_row * self.block_size + self.block_size // 2
        self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="blue", outline="") # Desenha o jogador na nova posição

        # Armazenar a posição anterior
        self.previous_position[(current_row, current_col)] = (current_row, current_col)

    def draw_solution(self, start_position, end_position, path):
        # Desenha o caminho mais longo encontrado no tabuleiro
        for i in range(len(path) - 1):
            current_row, current_col = path[i]
            next_row, next_col = path[i + 1]
            # Desenha uma linha entre a célula atual e a próxima célula no caminho
            self.canvas.create_line(
                current_col * self.block_size + self.block_size // 2,
                current_row * self.block_size + self.block_size // 2,
                next_col * self.block_size + self.block_size // 2,
                next_row * self.block_size + self.block_size // 2,
                fill="blue"
            )

# Define uma função para gerar uma grade aleatória com base na dificuldade selecionada
def generate_random_grid(difficulty):
    # Seleciona a grade apropriada com base na dificuldade
    if difficulty == "fácil":
        grids = maze_facil
    elif difficulty == "médio":
        grids = maze_medio
    elif difficulty == "difícil":
        grids = maze_dificil
    else:
        raise ValueError("Dificuldade inválida")

    return random.choice(grids) # Retorna uma grade aleatória da lista de grades disponíveis

# Define uma função para lidar com a seleção de dificuldade
def on_difficulty_selected(difficulty):
    # Gera uma grade aleatória com base na dificuldade selecionada
    grid = generate_random_grid(difficulty)

    # Modifica as cores das células de acordo com o padrão especificado
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] == 3:
                grid[i][j] = 4
            elif grid[i][j] == 2:
                grid[i][j] = 2
            else:
                grid[i][j] = grid[i][j] # Mantém as outras cores inalteradas

    # Altera a cor do canto inferior esquerdo para verde
    grid[-1][0] = 3
    # Altera a cor do canto superior direito para vermelho
    grid[0][-1] = 2

    # Cria uma instância da classe GridGUI com a grade gerada e exibe na interface gráfica
    grid_gui = GridGUI(root, grid)
    # Remove os botões de seleção de dificuldade após a seleção ser feita
    easy_button.pack_forget()
    medium_button.pack_forget()
    hard_button.pack_forget()


root = tk.Tk()  # Cria a janela principal da interface gráfica
root.title("Labirinto")  # Define o título da janela


# Defina as dimensões da janela para serem maiores
largura_janela = 400
altura_janela = 500
largura_ecra = root.winfo_screenwidth()
altura_ecra = root.winfo_screenheight()
pos_x = (largura_ecra - largura_janela) // 2
pos_y = (altura_ecra - altura_janela) // 2
root.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

# Cria botões para selecionar a dificuldade do jogo
easy_button = tk.Button(root, text="Fácil", command=lambda: on_difficulty_selected("fácil"), width=20, height=2, bg='black', fg='white', font=("Arial", 15))
easy_button.pack(pady=10)

medium_button = tk.Button(root, text="Médio", command=lambda: on_difficulty_selected("médio"), width=20, height=2, bg='black', fg='white', font=("Arial", 15))
medium_button.pack(pady=10)

hard_button = tk.Button(root, text="Difícil", command=lambda: on_difficulty_selected("difícil"), width=20, height=2, bg='black', fg='white', font=("Arial", 15))
hard_button.pack(pady=10)

# Inicia o loop principal da interface gráfica

root.mainloop()
