import json
import tkinter as tk
from tkinter import filedialog

class FileManager:
    def __init__(self):
        self.current_file = None

    def load(self):
        root = tk.Tk()
        root.withdraw()
        filename = filedialog.askopenfilename(
            title="Выберите файл с данными",
            filetypes=[("JSON Files", "*.json"), ("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not filename:
            return None, None
        try:
            if filename.lower().endswith(".json"):
                with open(filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                grid_size = data.get("grid_size")
                board = data.get("board")
                self.current_file = filename
                return grid_size, board
            elif filename.lower().endswith(".csv"):
                board = []
                with open(filename, "r", encoding="utf-8") as f:
                    for line in f:
                        row = list(map(int, line.strip().split(",")))
                        board.append(row)
                grid_size = len(board)
                self.current_file = filename
                return grid_size, board
        except Exception as e:
            print("Ошибка загрузки:", e)
            return None, None

    def save(self, filename, grid_size, board):
        try:
            if filename.lower().endswith(".json"):
                data = {"grid_size": grid_size, "board": board}
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
            elif filename.lower().endswith(".csv"):
                with open(filename, "w", encoding="utf-8") as f:
                    for row in board:
                        line = ",".join(map(str, row))
                        f.write(line + "\n")
            self.current_file = filename
            return True
        except Exception as e:
            print("Ошибка сохранения:", e)
            return False
