import pygame
import sys
import math
import json
import tkinter as tk
from tkinter import filedialog
from gui.buttons import Button
from gui.text_input import TextInput

class MainWindow:
    def __init__(self, width=800, height=600, grid_size=8):
        # Параметры окна
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Интерфейс трассировки")
        self.clock = pygame.time.Clock()

        # Тема оформления (цвета)
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

        # Размер меню-бар
        self.menu_bar_height = 30

        # Отступы и размеры поля трассировки
        self.top_margin = self.menu_bar_height + 10  # учитываем меню
        self.bottom_margin = 40
        self.left_margin = 20
        self.board_size = 450  # размер поля трассировки

        # Поле трассировки
        self.board_x = self.left_margin
        self.board_y = self.top_margin
        self.board_rect = pygame.Rect(self.board_x, self.board_y, self.board_size, self.board_size)

        # Параметры сетки
        self.rows = self.grid_size
        self.cols = self.grid_size
        self.cell_size = self.board_rect.width // self.cols
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

        # Строка состояния
        self.status_message = ""
        self.hover_status = None
        self.status_font = pygame.font.SysFont("Segoe UI", 18)
        status_bar_height = 30
        self.status_bar_rect = pygame.Rect(
            10,
            self.height - self.bottom_margin,
            self.width - 20,
            status_bar_height
        )

        # Режимы работы: "obstacle" для установки препятствий, "combined" для установки точек A/B.
        self.current_mode = None
        self.combined_step = None

        # Текстовое поле для изменения размера
        self.text_input = None

        # Для работы с файлами
        self.current_file = None  # путь к открытому файлу (если есть)

        # Список кнопок и словарь для кнопок режимов (для анимации)
        self.buttons = []
        self.mode_buttons = {}  # ключи: "obstacle", "combined"
        self.setup_buttons()  # <-- теперь метод определён!

        # Таймер для анимации подсветки активного режима
        self.highlight_timer = 0

        # Инициализация верхнего меню
        self.init_menu()

    def setup_buttons(self):
        """
        Создает кнопки для управления полем.
        Разбито на две группы:
         1. Первая группа (две колонки):
            - Строка 0: "Препятствие" и "Убрать преп."
            - Строка 1: "Старт/Финиш" и "Убрать A/B"
         2. Вторая группа (объединённая колонка):
            - "Очистить всё", "Размер", "Трасс.", "Пошаг", "Стоп", "Загрузить", "Сохранить", "Новый файл"
        """
        button_height = 45
        spacing_v = 10  # вертикальный отступ
        spacing_h = 10  # горизонтальный отступ между колонками

        # Координаты для первой группы (две колонки)
        left_col_x = self.board_rect.right + 20
        right_col_x = left_col_x + 130 + spacing_h  # ширина кнопки = 130

        # Всего строк в первой группе = 2
        total_rows_first_group = 2
        group1_total_height = total_rows_first_group * button_height + (total_rows_first_group - 1) * spacing_v

        # Начало размещения первой группы – вертикально центрировано относительно поля
        start_y = self.board_rect.top + (self.board_rect.height - group1_total_height - 8 * (button_height + spacing_v)) // 2

        # Первая строка – кнопки для препятствий
        row_y = start_y
        btn_obstacle = Button(
            left_col_x, row_y,
            130, button_height,
            "Препятствие",
            self.set_mode_obstacle,
            tooltip="Установить препятствие (ЛКМ)"
        )
        btn_clear_obstacles = Button(
            right_col_x, row_y,
            130, button_height,
            "Убрать преп.",
            self.clear_obstacles,
            tooltip="Удалить только препятствия"
        )
        self.mode_buttons["obstacle"] = btn_obstacle

        # Вторая строка – кнопки для точек старта/финиша
        row_y += button_height + spacing_v
        btn_startend = Button(
            left_col_x, row_y,
            130, button_height,
            "Старт/Финиш",
            self.set_mode_startend,
            tooltip="Установить ячейки A и B"
        )
        btn_clear_startend = Button(
            right_col_x, row_y,
            130, button_height,
            "Убрать A/B",
            self.clear_startend,
            tooltip="Удалить точки старта и финиша"
        )
        self.mode_buttons["combined"] = btn_startend

        # Вторая группа – объединённая колонка
        combined_width = 130 * 2 + spacing_h
        group2_start_y = row_y + button_height + spacing_v

        btn_clear_all = Button(
            left_col_x, group2_start_y,
            combined_width, button_height,
            "Очистить всё",
            self.clear_board,
            tooltip="Сбросить поле (препятствия и точки)"
        )
        btn_size = Button(
            left_col_x, group2_start_y + (button_height + spacing_v),
            combined_width, button_height,
            "Размер",
            self.activate_size_input,
            tooltip="Изменить размер поля"
        )
        btn_trace = Button(
            left_col_x, group2_start_y + 2*(button_height + spacing_v),
            combined_width, button_height,
            "Трасс.",
            self.start_tracing,
            tooltip="Запустить трассировку"
        )
        btn_step_trace = Button(
            left_col_x, group2_start_y + 3*(button_height + spacing_v),
            combined_width, button_height,
            "Пошаг",
            self.step_trace,
            tooltip="Пошаговая трассировка"
        )
        btn_stop_trace = Button(
            left_col_x, group2_start_y + 4*(button_height + spacing_v),
            combined_width, button_height,
            "Стоп",
            self.stop_tracing,
            tooltip="Остановить трассировку"
        )
        btn_load = Button(
            left_col_x, group2_start_y + 5*(button_height + spacing_v),
            combined_width, button_height,
            "Загрузить",
            self.load_board_data,
            tooltip="Загрузить данные поля из файла"
        )
        btn_save = Button(
            left_col_x, group2_start_y + 6*(button_height + spacing_v),
            combined_width, button_height,
            "Сохранить",
            self.save_board_data,
            tooltip="Сохранить изменения в файл"
        )
        btn_new = Button(
            left_col_x, group2_start_y + 7*(button_height + spacing_v),
            combined_width, button_height,
            "Новый файл",
            self.new_file,
            tooltip="Создать новый файл (очистить поле)"
        )

        self.buttons.extend([
            btn_obstacle,
            btn_clear_obstacles,
            btn_startend,
            btn_clear_startend,
            btn_clear_all,
            btn_size,
            btn_trace,
            btn_step_trace,
            btn_stop_trace,
            btn_load,
            btn_save,
            btn_new
        ])

    def init_menu(self):
        """Инициализирует структуру верхнего меню."""
        self.menu_items = {
            "Файл": [
                ("Новый файл", self.new_file),
                ("Открыть", self.load_board_data),
                ("Сохранить", self.save_board_data),
                ("Выход", sys.exit)
            ],
            "Правка": [
                ("Очистить всё", self.clear_board),
                ("Очистить преп.", self.clear_obstacles),
                ("Очистить A/B", self.clear_startend),
                ("Размер", self.activate_size_input)
            ],
            "Трассировка": [
                ("Трасс.", self.start_tracing),
                ("Пошаг", self.step_trace),
                ("Стоп", self.stop_tracing)
            ]
        }
        self.menu_positions = {}
        self.active_menu = None
        self.active_menu_items = []

    def draw_menu_bar(self):
        """Отрисовывает строку меню в верхней части окна."""
        menu_rect = pygame.Rect(0, 0, self.width, self.menu_bar_height)
        pygame.draw.rect(self.screen, self.theme["menu_bg"], menu_rect)
        font = pygame.font.SysFont("Segoe UI", 18)
        padding = 10
        x_offset = padding
        self.menu_positions = {}
        for menu_title in self.menu_items.keys():
            text_surf = font.render(menu_title, True, self.theme["menu_text"])
            text_rect = text_surf.get_rect(topleft=(x_offset, (self.menu_bar_height - text_surf.get_height()) // 2))
            self.screen.blit(text_surf, text_rect)
            self.menu_positions[menu_title] = pygame.Rect(x_offset, 0, text_rect.width, self.menu_bar_height)
            x_offset += text_rect.width + 2 * padding
        if self.active_menu:
            self.draw_dropdown(self.active_menu)

    def draw_dropdown(self, menu_title):
        """Отрисовывает выпадающее меню для выбранного пункта."""
        items = self.menu_items[menu_title]
        font = pygame.font.SysFont("Segoe UI", 16)
        dropdown_width = 150
        item_height = 25
        menu_rect = self.menu_positions[menu_title]
        dropdown_x = menu_rect.x
        dropdown_y = menu_rect.bottom
        dropdown_rect = pygame.Rect(dropdown_x, dropdown_y, dropdown_width, item_height * len(items))
        pygame.draw.rect(self.screen, self.theme["menu_bg"], dropdown_rect)
        pygame.draw.rect(self.screen, self.theme["grid_color"], dropdown_rect, 1)
        self.active_menu_items = []
        for index, (item_text, callback) in enumerate(items):
            item_rect = pygame.Rect(dropdown_x, dropdown_y + index * item_height, dropdown_width, item_height)
            if item_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(self.screen, self.theme["menu_hover"], item_rect)
            text_surf = font.render(item_text, True, self.theme["menu_text"])
            text_rect = text_surf.get_rect()
            text_rect.centery = item_rect.centery
            text_rect.x = item_rect.x + 5
            self.screen.blit(text_surf, text_rect)
            self.active_menu_items.append((item_text, item_rect, callback))

    def handle_menu_event(self, event):
        """Обрабатывает клики в меню."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for title, rect in self.menu_positions.items():
                if rect.collidepoint(pos):
                    if self.active_menu == title:
                        self.active_menu = None
                    else:
                        self.active_menu = title
                    return True
            if self.active_menu:
                for item_text, item_rect, callback in self.active_menu_items:
                    if item_rect.collidepoint(pos):
                        callback()
                        self.active_menu = None
                        return True
                self.active_menu = None
        return False

    def clear_board(self):
        """Полностью очищает поле (препятствия и точки)."""
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.set_status("Поле очищено")
        self.current_mode = None
        self.combined_step = None

    def clear_obstacles(self):
        """Удаляет препятствия (ячейки со значением 1)."""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] == 1:
                    self.board[row][col] = 0
        self.set_status("Все препятствия удалены")

    def clear_startend(self):
        """Удаляет точки старта и финиша (ячейки 2 и 3) и сбрасывает режим."""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] in (2, 3):
                    self.board[row][col] = 0
        self.current_mode = None
        self.combined_step = None
        self.set_status("Старт и конец удалены")

    def activate_size_input(self):
        """Активирует текстовое поле для ввода нового размера сетки."""
        input_width = 80
        input_height = 35
        last_button = self.buttons[-1]
        new_y = last_button.rect.bottom + 20
        self.text_input = TextInput(
            last_button.rect.x,
            new_y,
            input_width,
            input_height,
            font_size=20,
            initial_text=str(self.grid_size)
        )
        self.set_status("Введите число ячеек и нажмите Enter")

    def load_board_data(self):
        """Загружает данные поля из файла (JSON или CSV)."""
        root = tk.Tk()
        root.withdraw()
        filename = filedialog.askopenfilename(
            title="Выберите файл с данными",
            filetypes=[("JSON Files", "*.json"), ("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not filename:
            self.set_status("Файл не выбран")
            return
        try:
            if filename.lower().endswith(".json"):
                with open(filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                new_size = data.get("grid_size", self.grid_size)
                new_board = data.get("board", self.board)
            elif filename.lower().endswith(".csv"):
                new_board = []
                with open(filename, "r", encoding="utf-8") as f:
                    for line in f:
                        row = list(map(int, line.strip().split(",")))
                        new_board.append(row)
                new_size = len(new_board)
            else:
                self.set_status("Неподдерживаемый формат файла")
                return
            self.grid_size = new_size
            self.rows = new_size
            self.cols = new_size
            self.board = new_board
            self.cell_size = self.board_rect.width // self.cols
            self.current_file = filename
            self.set_status("Данные загружены из файла")
        except Exception as e:
            self.set_status(f"Ошибка загрузки: {e}")

    def save_board_data(self):
        """Сохраняет данные поля в файл (JSON или CSV)."""
        if self.current_file:
            filename = self.current_file
        else:
            root = tk.Tk()
            root.withdraw()
            filename = filedialog.asksaveasfilename(
                title="Сохранить файл",
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json"), ("CSV Files", "*.csv"), ("All Files", "*.*")]
            )
            if not filename:
                self.set_status("Сохранение отменено")
                return
            self.current_file = filename
        try:
            if filename.lower().endswith(".json"):
                data = {
                    "grid_size": self.grid_size,
                    "board": self.board
                }
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
            elif filename.lower().endswith(".csv"):
                with open(filename, "w", encoding="utf-8") as f:
                    for row in self.board:
                        line = ",".join(map(str, row))
                        f.write(line + "\n")
            else:
                self.set_status("Неподдерживаемый формат для сохранения")
                return
            self.set_status("Данные сохранены")
        except Exception as e:
            self.set_status(f"Ошибка сохранения: {e}")

    def new_file(self):
        """Создает новый файл (очищает поле и сбрасывает путь к файлу)."""
        self.clear_board()
        self.current_file = None
        self.set_status("Создан новый файл (поле очищено)")

    def set_mode_obstacle(self):
        """Включает режим установки препятствий."""
        self.current_mode = "obstacle"
        self.combined_step = None
        self.set_status("Режим: установка препятствия (ЛКМ)")

    def set_mode_startend(self):
        """Включает режим установки точек старта/финиша."""
        start_exists = any(cell == 2 for row in self.board for cell in row)
        end_exists = any(cell == 3 for row in self.board for cell in row)
        if start_exists and end_exists:
            self.set_status("Старт и конец уже установлены. Очистите поле для нового выбора.")
            return
        self.current_mode = "combined"
        self.combined_step = "start"
        self.set_status("Выберите ячейку для старта (A)")

    def start_tracing(self):
        """Запускает алгоритм трассировки."""
        self.set_status("Запущена трассировка")
        print("Запущена трассировка")

    def step_trace(self):
        """Запускает пошаговую трассировку."""
        self.set_status("Пошаговая трассировка запущена")
        print("Пошаговая трассировка")

    def stop_tracing(self):
        """Останавливает трассировку."""
        self.set_status("Трассировка остановлена")
        print("Трассировка остановлена")

    def update_board_size(self, new_size):
        """Обновляет размер сетки и пересоздает поле."""
        self.grid_size = new_size
        self.rows = new_size
        self.cols = new_size
        self.cell_size = self.board_rect.width // self.cols
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.set_status(f"Размер поля обновлён: {new_size}x{new_size}")

    def draw_board(self):
        """Отрисовывает поле трассировки и его содержимое."""
        pygame.draw.rect(self.screen, self.theme["board_bg"], self.board_rect, border_radius=10)
        for row in range(self.rows):
            for col in range(self.cols):
                rect = pygame.Rect(
                    self.board_rect.x + col * self.cell_size,
                    self.board_rect.y + row * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                cell_val = self.board[row][col]
                if cell_val == 1:
                    pygame.draw.rect(self.screen, (160, 160, 160), rect, border_radius=5)
                elif cell_val == 2:
                    pygame.draw.rect(self.screen, self.theme["board_bg"], rect)
                    font = pygame.font.SysFont("Segoe UI", self.cell_size - 4)
                    text_surf = font.render("A", True, (0, 0, 0))
                    text_rect = text_surf.get_rect(center=rect.center)
                    self.screen.blit(text_surf, text_rect)
                elif cell_val == 3:
                    pygame.draw.rect(self.screen, self.theme["board_bg"], rect)
                    font = pygame.font.SysFont("Segoe UI", self.cell_size - 4)
                    text_surf = font.render("B", True, (0, 0, 0))
                    text_rect = text_surf.get_rect(center=rect.center)
                    self.screen.blit(text_surf, text_rect)
                pygame.draw.rect(self.screen, self.theme["grid_color"], rect, 1)

    def draw_status_bar(self):
        """Отрисовывает строку состояния в нижней части окна."""
        pygame.draw.rect(self.screen, self.theme["status_bg"], self.status_bar_rect, border_radius=5)
        msg = self.hover_status if self.hover_status else self.status_message
        text_surf = self.status_font.render(msg, True, (0, 0, 0))
        self.screen.blit(
            text_surf,
            (
                self.status_bar_rect.x + 10,
                self.status_bar_rect.y + (self.status_bar_rect.height - text_surf.get_height()) // 2
            )
        )

    def handle_board_click(self, pos):
        """Обрабатывает клики по полю (в зависимости от выбранного режима)."""
        if not self.board_rect.collidepoint(pos):
            return
        col = (pos[0] - self.board_rect.x) // self.cell_size
        row = (pos[1] - self.board_rect.y) // self.cell_size
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return
        if self.current_mode == "obstacle":
            if self.board[row][col] in (2, 3):
                return
            if self.board[row][col] == 0:
                self.board[row][col] = 1
                self.set_status(f"Препятствие установлено в ({row}, {col})")
            elif self.board[row][col] == 1:
                self.board[row][col] = 0
                self.set_status(f"Препятствие удалено в ({row}, {col})")
        elif self.current_mode == "combined":
            if self.combined_step == "start":
                if self.board[row][col] == 0:
                    self.board[row][col] = 2
                    self.combined_step = "end"
                    self.set_status("Старт установлен. Выберите ячейку для конца (B)")
            elif self.combined_step == "end":
                if self.board[row][col] == 0:
                    self.board[row][col] = 3
                    self.current_mode = None
                    self.combined_step = None
                    self.set_status("Старт и конец установлены")

    def set_status(self, message):
        """Устанавливает сообщение в строке состояния и выводит его в консоль."""
        self.status_message = message
        print(message)

    def run(self):
        """Главный цикл приложения."""
        running = True
        while running:
            dt = self.clock.tick(60)
            self.highlight_timer += dt
            self.hover_status = None
            mouse_pos = pygame.mouse.get_pos()

            # Обработка событий меню
            for event in pygame.event.get():
                if self.handle_menu_event(event):
                    continue
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.board_rect.collidepoint(event.pos):
                        self.handle_board_click(event.pos)
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
                        self.set_status("Введите положительное число.")
                except ValueError:
                    self.set_status("Неверный ввод. Введите число.")
                self.text_input = None

            if self.text_input:
                self.text_input.update(dt)

            self.screen.fill(self.theme["background"])
            self.draw_board()
            for button in self.buttons:
                button.draw(self.screen)

            # Анимация подсветки выбранного режима
            if self.current_mode in self.mode_buttons:
                active_button = self.mode_buttons[self.current_mode]
                pulse = 2 + int(2 * (math.sin(self.highlight_timer * 0.005) + 1) / 2)
                highlight_rect = active_button.rect.inflate(6, 6)
                pygame.draw.rect(self.screen, self.theme["button"]["active_border"],
                                 highlight_rect, pulse, border_radius=active_button.rect.height // 4)

            if self.text_input:
                self.text_input.draw(self.screen)
            self.draw_status_bar()
            self.draw_menu_bar()
            pygame.display.flip()

        pygame.quit()
        sys.exit()
