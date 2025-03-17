import pygame, sys
import tkinter as tk
from tkinter import filedialog, simpledialog
from gui.buttons import Button
from gui.text_input import TextInput
from gui.board import Board
from gui.menubar import MenuBar
from gui.file_manager import FileManager
from gui.tracer import Tracer

class MainWindow:
    def __init__(self, width=800, height=600, grid_size=8):
        self.width = width
        self.height = height
        self.grid_size = grid_size

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Интерфейс трассировки")
        self.clock = pygame.time.Clock()

        self.theme = {
            "background": (240, 240, 240),
            "board_bg": (250, 250, 250),
            "grid_color": (200, 200, 200),
            "status_bg": (220, 220, 220),
            "menu_bg": (200, 200, 200),
            "menu_hover": (180, 180, 180),
            "menu_text": (0, 0, 0),
            "button": {
                "normal": (70, 130, 180),
                "shadow": (50, 50, 50),
                "border": (255, 255, 255),
                "text": (255, 255, 255),
                "active_border": (255, 215, 0)
            }
        }

        self.menu_bar_height = 30
        self.top_margin = self.menu_bar_height + 10
        self.bottom_margin = 40
        self.left_margin = 20

        self.panel_width = 150
        self.board_size = self.width - self.left_margin - self.panel_width - 20

        self.board_rect = pygame.Rect(self.left_margin, self.top_margin, self.board_size, self.board_size)
        self.board = Board(self.board_rect, grid_size, self.theme)
        self.status_message = ""
        self.hover_status = ""
        self.status_font = pygame.font.SysFont("Segoe UI", 18)
        self.status_bar_rect = pygame.Rect(10, self.height - self.bottom_margin, self.width - 20, 30)

        self.current_mode = None
        self.combined_step = None
        self.text_input = None
        self.file_manager = FileManager()
        self.current_file = None

        self.highlight_timer = 0

        self.step_mode = False
        self.step_generator = None

        self.buttons = []
        self.mode_buttons = {}
        self.setup_buttons()
        self.direction_order = [("U", -1, 0), ("R", 0, 1), ("D", 1, 0), ("L", 0, -1)]

        self.menu_bar = MenuBar(self.width, self.menu_bar_height, self.theme)
        menu_callbacks = {
            "Новый файл": self.new_file,
            "Открыть": self.load_board_data,
            "Сохранить": self.save_board_data,
            "Очистить всё": self.clear_board,
            "Очистить преп.": self.clear_obstacles,
            "Очистить A/B": self.clear_startend,
            "Размер": self.activate_size_input,
            "Трасс.": self.start_tracing,
            "Пошаг. режим": self.activate_step_mode,
            "Шаг": self.perform_step,
            "Убрать тр." : self.clear_tracing()
        }
        self.menu_bar.set_callbacks(menu_callbacks)

    def setup_buttons(self):
        button_height = 45
        spacing_v = 10
        column_x = self.board_rect.right + 20
        total_buttons = 7
        group_total_height = total_buttons * button_height + (total_buttons - 1) * spacing_v
        start_y = self.board_rect.top + (self.board_rect.height - group_total_height) // 2

        btn_obstacle = Button(
            column_x, start_y, 130, button_height,
            "Препятствие", self.set_mode_obstacle,
            tooltip="Установить препятствие (ЛКМ)"
        )
        btn_clear_obstacles = Button(
            column_x, start_y + button_height + spacing_v, 130, button_height,
            "Убрать преп.", self.clear_obstacles,
            tooltip="Удалить препятствия"
        )
        btn_startend = Button(
            column_x, start_y + 2*(button_height + spacing_v), 130, button_height,
            "Старт/Финиш", self.set_mode_startend,
            tooltip="Установить A и B"
        )
        btn_step_mode = Button(
            column_x, start_y + 4*(button_height + spacing_v), 130, button_height,
            "Пошаг. режим", self.activate_step_mode,
            tooltip="Активировать пошаговую трассировку"
        )
        btn_step = Button(
            column_x, start_y + 5*(button_height + spacing_v), 130, button_height,
            "Шаг", self.perform_step,
            tooltip="Выполнить следующий шаг трассировки"
        )
        btn_clear_trace = Button(
            column_x,
            start_y + 6*(button_height + spacing_v),130,button_height,
            "Убрать тр.",self.clear_tracing,
            tooltip="Убрать визуализацию трассировки"
        )
        self.buttons.append(btn_clear_trace)
        btn_clear_startend = Button(
            column_x, start_y + 3*(button_height + spacing_v), 130, button_height,
            "Убрать A/B", self.clear_startend,
            tooltip="Удалить A и B"
        )

        self.mode_buttons["obstacle"] = btn_obstacle
        self.mode_buttons["combined"] = btn_startend

        self.buttons.extend([btn_obstacle, btn_clear_obstacles, btn_startend, btn_clear_startend,
                             btn_clear_trace, btn_step_mode, btn_step])

    def activate_step_mode(self):
        start = None
        finish = None
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                if self.board.board[r][c] == 2:
                    start = (r, c)
                elif self.board.board[r][c] == 3:
                    finish = (r, c)
        if not start or not finish:
            self.set_status("Не заданы и старт, и финиш")
            return

        # Копия поля
        prop_grid = [row.copy() for row in self.board.board]
        prop_grid[start[0]][start[1]] = 0
        prop_grid[finish[0]][finish[1]] = 0

        tracer = Tracer(prop_grid)
        self.step_generator = tracer.step_by_step_trace(start, finish)
        self.step_mode = True
        self.set_status("Пошаговый режим трассировки включён. Нажмите 'Шаг'.")

    def perform_step(self):
        if not self.step_mode or self.step_generator is None:
            self.set_status("Пошаговая трассировка не активирована.")
            return

        try:
            iteration, wave_start, wave_finish, meeting = next(self.step_generator)
            self.board.wave_start = wave_start
            self.board.wave_finish = wave_finish

            self.screen.fill(self.theme["background"])
            self.board.draw(self.screen)
            for button in self.buttons:
                button.draw(self.screen)
            if self.text_input:
                self.text_input.draw(self.screen)
            self.draw_status_bar()
            self.menu_bar.draw(self.screen)
            pygame.display.flip()

            self.set_status(f"Итерация {iteration} выполнена.")
            if meeting:
                self.set_status(f"Встреча волн в клетке {meeting}. Трассировка завершена.")
                start = None
                finish = None
                for r in range(self.board.rows):
                    for c in range(self.board.cols):
                        if self.board.board[r][c] == 2:
                            start = (r, c)
                        elif self.board.board[r][c] == 3:
                            finish = (r, c)
                if start is None or finish is None:
                    self.set_status("Старт и Финиш не найдены")
                    return
                path_s = Tracer.reconstruct_path(wave_start, start, meeting)
                path_f = Tracer.reconstruct_path(wave_finish, finish, meeting)
                path_f.reverse()
                full_path = path_s + path_f[1:]

                final_path_arrows = {}
                for i in range(1, len(full_path)):
                    r1, c1 = full_path[i - 1]
                    r2, c2 = full_path[i]
                    if r2 == r1 - 1:
                        arrow = "↑"
                    elif r2 == r1 + 1:
                        arrow = "↓"
                    elif c2 == c1 + 1:
                        arrow = "→"
                    elif c2 == c1 - 1:
                        arrow = "←"
                    else:
                        arrow = ""
                    final_path_arrows[full_path[i]] = arrow

                self.board.final_path_arrows = final_path_arrows

                for (r, c) in full_path:
                    if self.board.board[r][c] not in (2, 3):
                        self.board.board[r][c] = 5  # значение 5 для финального пути

                path_length = len(full_path) - 1
                self.set_status(f"Путь найден, сумма клеток пути: {path_length}")
                self.step_mode = False
                self.step_generator = None

        except StopIteration:
                    self.set_status("Пошаговая трассировка завершена.")
                    self.step_mode = False
                    self.step_generator = None


    def clear_tracing(self):
        """
        Убирает визуализацию трассировки (волны и путь).
        """
        self.board.wave_start = None
        self.board.wave_finish = None
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                if self.board.board[r][c] in (4, 5):
                    self.board.board[r][c] = 0
        self.set_status("Трассировка убрана")

    def clear_startend(self):
        """
        Убирает A и B, а также трассировку.
        """
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                if self.board.board[r][c] in (2, 3):
                    self.board.board[r][c] = 0
        self.clear_tracing()
        self.current_mode = None
        self.combined_step = None
        self.set_status("Старт/Финиш удалены")

    def clear_board(self):
        """
        Полностью очищает поле, включая путь и волны.
        """
        self.board.board = [[0 for _ in range(self.board.cols)] for _ in range(self.board.rows)]
        self.board.wave_start = None
        self.board.wave_finish = None
        self.current_mode = None
        self.combined_step = None
        self.set_status("Поле очищено")

    def clear_obstacles(self):
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                if self.board.board[r][c] == 1:
                    self.board.board[r][c] = 0
        self.set_status("Препятствия удалены")

    def activate_size_input(self):
        input_width = 80
        input_height = 35
        new_x = self.width - input_width - 20
        new_y = self.menu_bar_height + 5
        self.text_input = TextInput(new_x, new_y, input_width, input_height, 20, str(self.board.grid_size))
        self.set_status("Введите новый размер")

    def load_board_data(self):
        grid_size, board_data = self.file_manager.load()
        if grid_size and board_data:
            self.board.update_size(grid_size)
            self.board.board = board_data
            self.current_file = self.file_manager.current_file
            self.set_status("Данные загружены")

    def save_board_data(self):
        if self.current_file is None:
            root = tk.Tk()
            root.withdraw()
            filename = filedialog.asksaveasfilename(title="Сохранить", defaultextension=".json",
                                                    filetypes=[("JSON Files", "*.json"), ("CSV Files", "*.csv")])
            if not filename:
                self.set_status("Сохранение отменено")
                return
            self.current_file = filename
        if self.file_manager.save(self.current_file, self.board.grid_size, self.board.board):
            self.set_status("Данные сохранены")

    def new_file(self):
        self.clear_board()
        self.current_file = None
        self.set_status("Создан новый файл")

    def set_mode_obstacle(self):
        self.current_mode = "obstacle"
        self.combined_step = None
        self.set_status("Режим препятствий")

    def set_mode_startend(self):
        if any(cell == 2 for row in self.board.board for cell in row) and \
                any(cell == 3 for row in self.board.board for cell in row):
            self.set_status("Старт и Финиш уже установлены")
            return
        self.current_mode = "combined"
        self.combined_step = "start"
        self.set_status("Выберите старт (A)")

    def start_tracing(self):
        start = None
        finish = None
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                if self.board.board[r][c] == 2:
                    start = (r, c)
                elif self.board.board[r][c] == 3:
                    finish = (r, c)
        if start is None or finish is None:
            self.set_status("Не заданы и старт, и финиш")
            return

        grid_copy = [row.copy() for row in self.board.board]
        grid_copy[start[0]][start[1]] = 0
        grid_copy[finish[0]][finish[1]] = 0

        tracer = Tracer(grid_copy, direction_order=self.direction_order)
        wave_s, wave_f, meet = tracer.bidirectional_trace(start, finish)

        self.board.wave_start = wave_s
        self.board.wave_finish = wave_f

        if meet:
            self.set_status(f"Пересечение волн в {meet}")
            path_s = Tracer.reconstruct_path(wave_s, start, meet)
            path_f = Tracer.reconstruct_path(wave_f, finish, meet)
            path_f.reverse()
            full_path = path_s + path_f[1:]

            for (rr, cc) in full_path:
                if self.board.board[rr][cc] not in (2, 3):
                    self.board.board[rr][cc] = 5

            self.set_status(f"Путь найден, длина: {len(full_path) - 1}")
        else:
            self.set_status("Путь не найден")

    
    def stop_tracing(self):
        self.set_status("Трассировка остановлена")
        print("Трассировка остановлена")

    def update_board_size(self, new_size):
        self.board.update_size(new_size)
        self.set_status(f"Размер поля: {new_size}x{new_size}")

    def set_status(self, message):
        self.status_message = message
        print(message)

    def draw_status_bar(self):
        pygame.draw.rect(self.screen, self.theme["status_bg"], self.status_bar_rect, border_radius=5)
        text_surf = self.status_font.render(self.status_message, True, (0, 0, 0))
        self.screen.blit(text_surf, (self.status_bar_rect.x + 10,
                                     self.status_bar_rect.y + (self.status_bar_rect.height - text_surf.get_height()) // 2))

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60)
            self.highlight_timer += dt
            self.hover_status = ""
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if self.menu_bar.handle_event(event):
                    continue
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.board_rect.collidepoint(event.pos):
                        self.current_mode, self.combined_step = self.board.handle_click(
                            event.pos, self.current_mode, self.combined_step)
                for button in self.buttons:
                    button.handle_event(event)
                if self.text_input:
                    self.text_input.handle_event(event)

            if self.text_input and self.text_input.done:
                try:
                    new_size = int(self.text_input.text)
                    if new_size > 0:
                        self.update_board_size(new_size)
                    else:
                        self.set_status("Введите положительное число")
                except ValueError:
                    self.set_status("Неверный ввод")
                self.text_input = None
            if self.text_input:
                self.text_input.update(dt)

            self.screen.fill(self.theme["background"])
            self.board.draw(self.screen)
            for button in self.buttons:
                button.draw(self.screen)
            if self.text_input:
                self.text_input.draw(self.screen)
            self.draw_status_bar()
            self.menu_bar.draw(self.screen)
            pygame.display.flip()
        pygame.quit()
        sys.exit()

