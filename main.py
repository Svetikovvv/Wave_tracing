# main.py
import pygame
from gui.window import MainWindow

def main():
    pygame.init()
    app = MainWindow(width=800, height=600, grid_size=8)
    app.run()

if __name__ == "__main__":
    main()
