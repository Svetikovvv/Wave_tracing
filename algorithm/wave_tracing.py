# algorithm/wave_tracing.py

from collections import deque

class BiWaveTracer:

    def __init__(self, board, rows, cols, start, end, direction_priority):
        self.board = board
        self.rows = rows
        self.cols = cols
        self.start = start
        self.end = end
        self.direction_priority = direction_priority  # пользовательский приоритет направлений

        # Очереди для двунаправленного поиска
        self.queue_start = deque([start])
        self.queue_end = deque([end])
        # Родители для восстановления пути
        self.parents_start = {start: None}
        self.parents_end = {end: None}
        # Массивы visited
        self.visited_start = [[False]*cols for _ in range(rows)]
        self.visited_end = [[False]*cols for _ in range(rows)]
        self.visited_start[start[0]][start[1]] = True
        self.visited_end[end[0]][end[1]] = True

        self.meeting_point = None
        self.finished = False

    def step(self):
        if self.finished:
            return True  # уже закончено

        # Шаг волны от старта
        if self.queue_start and not self.meeting_point:
            qsize = len(self.queue_start)
            for _ in range(qsize):
                cur = self.queue_start.popleft()
                for d in self.direction_priority:
                    ni, nj = cur[0] + d[0], cur[1] + d[1]
                    if 0 <= ni < self.rows and 0 <= nj < self.cols:
                        if self.board[ni][nj] != 1 and not self.visited_start[ni][nj]:
                            self.visited_start[ni][nj] = True
                            self.parents_start[(ni, nj)] = cur
                            self.queue_start.append((ni, nj))
                            # Проверяем, не посещена ли эта клетка другой волной
                            if self.visited_end[ni][nj]:
                                self.meeting_point = (ni, nj)
                                break
                if self.meeting_point:
                    break

        # Шаг волны от финиша
        if self.queue_end and not self.meeting_point:
            qsize = len(self.queue_end)
            for _ in range(qsize):
                cur = self.queue_end.popleft()
                for d in self.direction_priority:
                    ni, nj = cur[0] + d[0], cur[1] + d[1]
                    if 0 <= ni < self.rows and 0 <= nj < self.cols:
                        if self.board[ni][nj] != 1 and not self.visited_end[ni][nj]:
                            self.visited_end[ni][nj] = True
                            self.parents_end[(ni, nj)] = cur
                            self.queue_end.append((ni, nj))
                            # Проверяем, не посещена ли эта клетка другой волной
                            if self.visited_start[ni][nj]:
                                self.meeting_point = (ni, nj)
                                break
                if self.meeting_point:
                    break

        # Проверяем, не закончился ли поиск
        if self.meeting_point:
            self.finished = True
            return True
        if not self.queue_start and not self.queue_end:
            # Волны исчерпаны, путь не найден
            self.finished = True
            return True

        return False

    def reconstruct_path(self):
        if not self.meeting_point:
            return None
        path = []
        cur = self.meeting_point
        while cur is not None:
            path.append(cur)
            cur = self.parents_start.get(cur)
        path.reverse()
        cur = self.parents_end.get(self.meeting_point)
        while cur is not None:
            path.append(cur)
            cur = self.parents_end.get(cur)
        return path
