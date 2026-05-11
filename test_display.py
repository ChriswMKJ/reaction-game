import pygame
import sys
import random
from datetime import datetime

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
width, height = screen.get_size()
pygame.display.set_caption("Reaction Game Prototype")

bg_color = (15, 15, 20)
title_color = (255, 255, 255)
status_color = (180, 180, 180)
accent_color = (80, 200, 120)

title_font = pygame.font.SysFont("Arial", 64)
status_font = pygame.font.SysFont("Arial", 32)
hint_font = pygame.font.SysFont("Arial", 24)

locations = [
    "Berlin",
    "Hamburg",
    "Muenchen",
    "Koeln",
    "Frankfurt",
    "Leipzig"
]

current_location = random.choice(locations)
status_text = "Warte auf Eingabe"
last_hit_ms = None

clock = pygame.time.Clock()

def draw():
    screen.fill(bg_color)

    title_surface = title_font.render(current_location, True, title_color)
    title_rect = title_surface.get_rect(center=(width // 2, height // 2 - 40))
    screen.blit(title_surface, title_rect)

    status_surface = status_font.render(status_text, True, accent_color)
    status_rect = status_surface.get_rect(center=(width // 2, height // 2 + 40))
    screen.blit(status_surface, status_rect)

    hint_lines = [
        "N = naechster Standort",
        "H = Treffer simulieren",
        "ESC = Beenden"
    ]

    y = height - 120
    for line in hint_lines:
        hint_surface = hint_font.render(line, True, status_color)
        hint_rect = hint_surface.get_rect(center=(width // 2, y))
        screen.blit(hint_surface, hint_rect)
        y += 30

    pygame.display.flip()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            elif event.key == pygame.K_n:
                current_location = random.choice(locations)
                status_text = "Neuer Standort gewaehlt"

            elif event.key == pygame.K_h:
                last_hit_ms = random.randint(250, 1500)
                status_text = f"Treffer! Reaktionszeit: {last_hit_ms} ms"

    draw()
    clock.tick(30)
