import tkinter as tk
from tkinter import messagebox
import socket
import json
import random

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000


class Game2048:
    def __init__(self, root):
        self.root = root
        self.root.title('2048 Game')

        self.username = None
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.connect((SERVER_HOST, SERVER_PORT))

        self.game_frame = tk.Frame(root)
        self.login_frame = tk.Frame(root)
        self.leaderboard_frame = tk.Frame(root)

        self.create_login_widgets()
        self.create_game_widgets()
        self.create_leaderboard_widgets()

    def create_login_widgets(self):
        self.login_frame.pack()

        self.username_label = tk.Label(self.login_frame, text='Username')
        self.username_label.grid(row=0, column=0)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1)

        self.password_label = tk.Label(self.login_frame, text='Password')
        self.password_label.grid(row=1, column=0)
        self.password_entry = tk.Entry(self.login_frame, show='*')
        self.password_entry.grid(row=1, column=1)

        self.login_button = tk.Button(self.login_frame, text='Login', command=self.login)
        self.login_button.grid(row=2, column=0)
        self.register_button = tk.Button(self.login_frame, text='Register', command=self.register)
        self.register_button.grid(row=2, column=1)

        self.status_label = tk.Label(self.login_frame, text='')
        self.status_label.grid(row=3, column=0, columnspan=2)

    def create_game_widgets(self):
        self.grid_frame = tk.Frame(self.game_frame)
        self.grid_frame.pack()

        self.tiles = {}
        for i in range(4):
            for j in range(4):
                tile = tk.Label(self.grid_frame, text='', width=4, height=2, font=('Arial', 24), borderwidth=2, relief='solid')
                tile.grid(row=i, column=j, padx=5, pady=5)
                self.tiles[(i, j)] = tile

        self.score = 0
        self.score_label = tk.Label(self.game_frame, text=f'Score: {self.score}', font=('Arial', 14))
        self.score_label.pack()

        self.restart_button = tk.Button(self.game_frame, text='Restart', command=self.restart_game)
        self.restart_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.leaderboard_button = tk.Button(self.game_frame, text='Leaderboard', command=self.show_leaderboard)
        self.leaderboard_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.logout_button = tk.Button(self.game_frame, text='Logout', command=self.logout)
        self.logout_button.pack(side=tk.LEFT, padx=5, pady=5)

    def create_leaderboard_widgets(self):
        self.leaderboard_frame.pack_forget()
        self.leaderboard_list = tk.Listbox(self.leaderboard_frame, width=50, height=10)
        self.leaderboard_list.pack(padx=10, pady=10)
        self.close_leaderboard_button = tk.Button(self.leaderboard_frame, text='Close', command=self.hide_leaderboard)
        self.close_leaderboard_button.pack(pady=5)

    def init_game(self):
        self.board = [[0] * 4 for _ in range(4)]
        self.add_new_tile()
        self.add_new_tile()
        self.update_display()
        self.bind_keys()

    def update_display(self):
        for (i, j), tile in self.tiles.items():
            value = self.board[i][j]
            tile.config(text=str(value) if value != 0 else '', bg=self.get_color(value))
        self.score_label.config(text=f'Score: {self.score}')

    def get_color(self, value):
        colors = {
            0: 'lightgray', 2: 'lightyellow', 4: 'lightblue', 8: 'lightgreen',
            16: 'lightcoral', 32: 'orange', 64: 'red', 128: 'pink',
            256: 'purple', 512: 'blue', 1024: 'green', 2048: 'gold'
        }
        return colors.get(value, 'black')

    def add_new_tile(self):
        empty_positions = [(i, j) for i in range(4) for j in range(4) if self.board[i][j] == 0]
        if empty_positions:
            i, j = random.choice(empty_positions)
            self.board[i][j] = random.choice([2, 4])
            self.update_display()

    def bind_keys(self):
        self.root.bind('<Up>', self.move_up)
        self.root.bind('<Down>', self.move_down)
        self.root.bind('<Left>', self.move_left)
        self.root.bind('<Right>', self.move_right)

    def move_up(self, event):
        self.move('up')

    def move_down(self, event):
        self.move('down')

    def move_left(self, event):
        self.move('left')

    def move_right(self, event):
        self.move('right')

    def move(self, direction):
        moved = False
        if direction == 'up':
            for j in range(4):
                column = [self.board[i][j] for i in range(4)]
                new_column, column_moved = self.merge(column)
                for i in range(4):
                    if self.board[i][j] != new_column[i]:
                        moved = True
                    self.board[i][j] = new_column[i]
        elif direction == 'down':
            for j in range(4):
                column = [self.board[i][j] for i in range(4)][::-1]
                new_column, column_moved = self.merge(column)
                for i in range(4):
                    if self.board[i][j] != new_column[3 - i]:
                        moved = True
                    self.board[i][j] = new_column[3 - i]
        elif direction == 'left':
            for i in range(4):
                row = self.board[i]
                new_row, row_moved = self.merge(row)
                if self.board[i] != new_row:
                    moved = True
                self.board[i] = new_row
        elif direction == 'right':
            for i in range(4):
                row = self.board[i][::-1]
                new_row, row_moved = self.merge(row)
                if self.board[i] != new_row[::-1]:
                    moved = True
                self.board[i] = new_row[::-1]

        if moved:
            self.add_new_tile()
            if self.is_game_over():
                self.end_game()

    def merge(self, line):
        new_line = [i for i in line if i != 0]
        for i in range(len(new_line) - 1):
            if new_line[i] == new_line[i + 1]:
                new_line[i] *= 2
                self.score += new_line[i]
                new_line[i + 1] = 0
        new_line = [i for i in new_line if i != 0]
        return new_line + [0] * (4 - len(new_line)), len(new_line) != len(line)

    def is_game_over(self):
        for i in range(4):
            for j in range(4):
                if self.board[i][j] == 0:
                    return False
                if i < 3 and self.board[i][j] == self.board[i + 1][j]:
                    return False
                if j < 3 and self.board[i][j] == self.board[i][j + 1]:
                    return False
        return True

    def end_game(self):
        self.send_score_to_server()
        messagebox.showinfo('Game Over', f'Game Over! Your score is {self.score}')
        self.restart_game()

    def send_request_to_server(self, request):
        try:
            self.server_socket.send(json.dumps(request).encode('utf-8'))
            response = self.server_socket.recv(1024).decode('utf-8')
            return json.loads(response)
        except Exception as e:
            messagebox.showerror('Error', f'Failed to communicate with server: {e}')
            return None

    def send_score_to_server(self):
        request = {
            'action': 'submit_score',
            'username': self.username,
            'score': self.score
        }
        response = self.send_request_to_server(request)
        if response and response.get('status') == 'success':
            new_high_score = response.get('new_high_score', False)
            if new_high_score:
                messagebox.showinfo('New High Score!', f'Congratulations! You achieved a new high score: {self.score}')

    def show_leaderboard(self):
        request = {'action': 'get_leaderboard'}
        response = self.send_request_to_server(request)
        if response and response.get('status') == 'success':
            self.leaderboard_list.delete(0, tk.END)
            for entry in response['leaderboard']:
                self.leaderboard_list.insert(tk.END, f"{entry['username']}: {entry['high_score']}")
            self.game_frame.pack_forget()
            self.leaderboard_frame.pack()

    def hide_leaderboard(self):
        self.leaderboard_frame.pack_forget()
        self.game_frame.pack()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        request = {
            'action': 'login',
            'username': username,
            'password': password
        }
        response = self.send_request_to_server(request)
        if response and response.get('status') == 'success':
            self.username = username
            self.login_frame.pack_forget()
            self.game_frame.pack()
            self.init_game()
        else:
            self.status_label.config(text='Login failed')

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        request = {
            'action': 'register',
            'username': username,
            'password': password
        }
        response = self.send_request_to_server(request)
        if response and response.get('status') == 'success':
            self.status_label.config(text='Registration successful')
        else:
            self.status_label.config(text='Registration failed')

    def restart_game(self):
        self.score = 0
        self.init_game()

    def logout(self):
        self.game_frame.pack_forget()
        self.login_frame.pack()
        self.username = None


if __name__ == '__main__':
    root = tk.Tk()
    game = Game2048(root)
    root.mainloop()
