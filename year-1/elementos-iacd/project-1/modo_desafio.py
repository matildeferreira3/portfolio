import tkinter as tk
import random
from tkinter import messagebox
from collections import deque
from PIL import ImageTk, Image, ImageFilter  # Importe do módulo Pillow para trabalhar com imagens
from tabuleiros import maze_dificil, maze_facil, maze_medio
import threading 
import time


class DesafioGUI:
    def __init__(self, master, grid):
        self.master = master
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.block_size = 50
        self.colors = {0: "white", 1: "black", 2: "red", 3: "green", 4: "blue", 5: "yellow"}  
        self.player_color = "blue"
        self.player_size = 40  
        self.player_position = (len(grid)-1, 0)  
        self.visited = set()  
        self.canvas = tk.Canvas(master, width=self.cols * self.block_size, height=self.rows * self.block_size)
        self.canvas.pack()
        self.btn_resolver = tk.Button(master, text="Resolver", command=self.resolver_tabuleiro_desafio, bg='black', fg='white', font=("Arial", 15))
        self.btn_resolver.pack(pady=10)
        self.btn_tentar_novamente = tk.Button(master, text="Tentar Novamente", command=self.reset_game_desafio, bg='black', fg='white', font=("Arial", 15))
        self.btn_tentar_novamente.pack(pady=10)
        self.previous_position = {}  # Alterando para um dicionário vazio para armazenar as posições anteriores
        self.draw_grid_desafio()
        self.draw_player_desafio()
        self.previous_position = None  # Inicialize previous_position como None

        self.master.bind("<KeyPress>", self.move_player_desafio)

        self.time_remaining = 25 #25 segundos

        # Crie um rótulo para exibir o cronômetro
        self.lbl_timer = tk.Label(master, text="Tempo restante: 25 segundos", font=("Arial", 12))
        self.lbl_timer.pack()

        # Inicie uma nova thread para o cronômetro
        self.timer_thread = threading.Thread(target=self.update_timer)
        self.timer_thread.daemon = True  # Encerrará a thread quando a janela for fechada
        self.timer_thread.start()


    def update_timer(self):
        while self.time_remaining > 0:
            # Atualize o rótulo do cronômetro com o tempo restante
            self.lbl_timer.config(text=f"Tempo restante: {self.time_remaining} segundos")
            # Aguarde 1 segundo
            self.time_remaining -= 1
            time.sleep(1)
        
        # Se o tempo acabar, exiba uma mensagem de derrota
        messagebox.showinfo("Derrota", "Tempo esgotado! Não conseguiste completar o labirinto a tempo.")
        # Encerre o jogo
        self.master.quit()

    def draw_grid_desafio(self):
        for row in range(self.rows):
            for col in range(self.cols):
                x0 = col * self.block_size
                y0 = row * self.block_size
                x1 = x0 + self.block_size
                y1 = y0 + self.block_size
                
                # Mapeia os valores numéricos para as cores correspondentes
                color = self.colors[self.grid[row][col]]
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="black")

    def draw_player_desafio(self):
        row, col = self.player_position
        x0 = col * self.block_size + (self.block_size - self.player_size) // 2  # Centraliza o jogador horizontalmente
        y0 = row * self.block_size + (self.block_size - self.player_size) // 2  # Centraliza o jogador verticalmente
        x1 = x0 + self.player_size
        y1 = y0 + self.player_size
        self.player = self.canvas.create_oval(x0, y0, x1, y1, fill=self.player_color)

    def check_game_state_desafio(self):
        # Verifica se o jogador está na célula de saída
        if self.player_position == (0, self.cols - 1):
            # Marca a célula de saída como vermelha
            self.grid[0][self.cols - 1] = 2

            # Verifica se todas as células do tabuleiro foram visitadas
            if len(self.visited) == (self.rows * self.cols) - sum(row.count(1) for row in self.grid):
                messagebox.showinfo("Vitória!", "Parabéns! Terminaste o tabuleiro.")
                self.master.quit()
                return True
            else:
                # Mensagem de derrota com dois botões
                result = messagebox.askquestion("Derrota", "Não passaste por todas as células! Game Over.\nQueres tentar novamente?")
                if result == 'yes':  # Se o jogador escolher tentar novamente
                    self.reset_game_desafio()
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
            self.reset_game_desafio()
        else:  # Se o jogador escolher fechar o jogo
            self.master.quit()

        # Marca a célula de saída como vermelha
        self.grid[0][self.cols - 1] = 2
        return True


    
    def move_player_desafio(self, event):
        key = event.keysym
        row, col = self.player_position
        new_row, new_col = row, col  # Definindo inicialmente as novas posições como as atuais

        if key == "Up" or key == "w":
            new_row = row - 1
        elif key == "Down" or key == "s":
            new_row = row + 1
        elif key == "Left" or key == "a":
            new_col = col - 1
        elif key == "Right" or key == "d":
            new_col = col + 1
        
        # Verifica se o movimento é válido antes de atualizar a posição do jogador
        if 0 <= new_row < self.rows and 0 <= new_col < self.cols and self.grid[new_row][new_col] != 1 and (new_row, new_col) not in self.visited:
            # Marca a posição inicial como visitada automaticamente após o jogador sair dela pela primeira vez
            if self.player_position == (self.rows - 1, 0):
                self.visited.add(self.player_position)
            # Verifica se o jogador não está tentando voltar para a posição inicial
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
                if self.check_game_state_desafio():
                    return

    def reset_game_desafio(self):
        # Reiniciar todos os atributos relevantes
        self.visited = set()
        self.longest_path = []
        self.longest_path_length = 0

        # Limpar as células pintadas de amarelo
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == 5:
                    self.grid[row][col] = 0
                    x0 = col * self.block_size
                    y0 = row * self.block_size
                    x1 = x0 + self.block_size
                    y1 = y0 + self.block_size
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill="white", outline="black")

        # Redesenhar o jogador na posição inicial
        self.player_position = (len(self.grid) - 1, 0)
        self.draw_player_desafio()

        # Garantir que a célula de saída seja vermelha
        self.grid[0][self.cols - 1] = 2

    def resolver_tabuleiro_desafio(self):
        self.reset_game_desafio()
        def is_valid(row, col):
            return 0 <= row < self.rows and 0 <= col < self.cols and self.grid[row][col] != 1

        def get_valid_neighbors_desafio(row, col):
            valid_neighbors = []
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_row, new_col = row + dr, col + dc
                if is_valid(new_row, new_col) and (new_row, new_col) not in self.visited:
                    valid_neighbors.append((new_row, new_col))
            return valid_neighbors

        def dfs(current_row, current_col, path_length, path):
            if (current_row, current_col) == (0, self.cols - 1):
                if path_length > self.longest_path_length:
                    self.longest_path_length = path_length
                    self.longest_path = list(path)
                return

            for neighbor_row, neighbor_col in get_valid_neighbors_desafio(current_row, current_col):
                path.append((neighbor_row, neighbor_col))
                self.visited.add((neighbor_row, neighbor_col))
                dfs(neighbor_row, neighbor_col, path_length + 1, path)
                path.pop()
                self.visited.remove((neighbor_row, neighbor_col))

        self.longest_path = []
        self.longest_path_length = 0
        start_row, start_col = self.rows - 1, 0
        dfs(start_row, start_col, 1, [(start_row, start_col)])

        # Draw the longest path found
        if self.longest_path:
            start_position = (start_row, start_col)
            end_position = (0, self.cols - 1)
            self.draw_solution_desafio(start_position, end_position, self.longest_path)
            # Após encontrar a solução, redefina o jogo para permitir que o jogador tente novamente
            self.reset_game_desafio()


    def update_gui_desafio(self, current_row, current_col):
        x = current_col * self.block_size + self.block_size // 2
        y = current_row * self.block_size + self.block_size // 2
        self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="blue", outline="")

        # Armazenar a posição anterior
        self.previous_position[(current_row, current_col)] = (current_row, current_col)

    def draw_solution_desafio(self, start_position, end_position, path):
        for i in range(len(path) - 1):
            current_row, current_col = path[i]
            next_row, next_col = path[i + 1]
            self.canvas.create_line(
                current_col * self.block_size + self.block_size // 2,
                current_row * self.block_size + self.block_size // 2,
                next_col * self.block_size + self.block_size // 2,
                next_row * self.block_size + self.block_size // 2,
                fill="blue"
            )
def generate_random_grid_desafio(difficulty):
    return random.choice(maze_dificil)

def on_difficulty_selected(difficulty="dificil"):
    grid = generate_random_grid_desafio(difficulty)

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] == 3:
                grid[i][j] = 4
            elif grid[i][j] == 2:
                grid[i][j] = 2
            else:
                grid[i][j] = grid[i][j]

    # Altera a cor do canto inferior esquerdo para verde
    grid[-1][0] = 3
    # Altera a cor do canto superior esquerdo para vermelho
    grid[0][-1] = 2

    grid_gui = DesafioGUI(root, grid)


    
root = tk.Tk()
root.title("Labirinto")

on_difficulty_selected()

root.mainloop()