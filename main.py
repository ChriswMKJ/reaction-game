import json
import os
import random
import sys
import time

import pygame


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "locations.json")
IMAGE_DIR = os.path.join(BASE_DIR, "assets", "images")

SCREEN_WIDTH = 0
SCREEN_HEIGHT = 0
GAME_DURATION_SECONDS = 30
COUNTDOWN_SECONDS = 3
FPS = 30

COLORS = {
    "background": (18, 18, 24),
    "text": (245, 245, 245),
    "subtle": (180, 180, 190),
    "accent": (255, 255, 255),
    "moebelhaus": (220, 50, 50),
    "logistik": (40, 110, 220),
    "lager": (40, 170, 80),
    "zentrale": (230, 140, 20),
    "unknown": (120, 120, 120),
    "panel": (28, 28, 36),
}

TYPE_LABELS = {
    "moebelhaus": "Moebelhaus",
    "logistik": "Logistik-Service-Center",
    "lager": "Zentrallager / E-Commerce-Lager",
    "zentrale": "Zentrale",
}


def load_locations():
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"Datei nicht gefunden: {DATA_FILE}")

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    active_locations = [loc for loc in data if loc.get("active", False)]

    if not active_locations:
        raise ValueError("Keine aktiven Standorte in locations.json gefunden.")

    return active_locations


def get_type_color(location_type):
    return COLORS.get(location_type, COLORS["unknown"])


def get_type_label(location_type):
    return TYPE_LABELS.get(location_type, location_type)


def load_image(filename, max_width, max_height):
    if not filename:
        return None

    image_path = os.path.join(IMAGE_DIR, filename)

    if not os.path.exists(image_path):
        return None

    try:
        image = pygame.image.load(image_path)
        image = image.convert()

        width, height = image.get_size()
        scale = min(max_width / width, max_height / height)
        scale = min(scale, 1.0)

        new_size = (int(width * scale), int(height * scale))
        image = pygame.transform.smoothscale(image, new_size)
        return image
    except Exception:
        return None


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        self.width, self.height = self.screen.get_size()
        pygame.display.set_caption("Reaction Game Prototype")

        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont("Arial", 54, bold=True)
        self.font_large = pygame.font.SysFont("Arial", 110, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", 36, bold=False)
        self.font_small = pygame.font.SysFont("Arial", 24, bold=False)

        self.all_locations = load_locations()

        self.state = "menu"
        self.score = 0
        self.round_pool = []
        self.current_location = None
        self.current_image = None
        self.game_start_time = None
        self.countdown_start_time = None
        self.message = ""
        self.last_action_time = 0

    def reset_game(self):
        self.score = 0
        self.round_pool = self.all_locations.copy()
        random.shuffle(self.round_pool)
        self.current_location = None
        self.current_image = None
        self.game_start_time = None
        self.countdown_start_time = None
        self.message = ""

    def start_countdown(self):
        self.reset_game()
        self.state = "countdown"
        self.countdown_start_time = time.time()

    def start_playing(self):
        self.state = "playing"
        self.game_start_time = time.time()
        self.next_location()

    def next_location(self):
        if not self.round_pool:
            self.current_location = None
            self.current_image = None
            self.message = "Keine weiteren Standorte in dieser Runde."
            return

        self.current_location = self.round_pool.pop()
        self.current_image = load_image(
            self.current_location.get("image", ""),
            max_width=int(self.width * 0.42),
            max_height=int(self.height * 0.55),
        )
        self.message = "Standort aktiv"

    def finish_game(self):
        self.state = "game_over"

    def remaining_time(self):
        if self.game_start_time is None:
            return GAME_DURATION_SECONDS
        elapsed = time.time() - self.game_start_time
        return max(0, GAME_DURATION_SECONDS - elapsed)

    def handle_hit(self):
        if self.state != "playing" or self.current_location is None:
            return

        self.score += 1
        self.message = f"Treffer! +1 Punkt | Button {self.current_location.get('button_id')}"
        self.next_location()

    def handle_skip(self):
        if self.state != "playing" or self.current_location is None:
            return

        self.message = "Uebersprungen"
        self.next_location()

    def draw_text_center(self, text, font, color, y):
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(self.width // 2, y))
        self.screen.blit(surface, rect)

    def draw_wrapped_text(self, text, font, color, x, y, max_width, line_spacing=8):
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = word if current_line == "" else current_line + " " + word
            test_surface = font.render(test_line, True, color)
            if test_surface.get_width() <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        current_y = y
        for line in lines:
            surface = font.render(line, True, color)
            self.screen.blit(surface, (x, current_y))
            current_y += surface.get_height() + line_spacing

    def draw_menu(self):
        self.screen.fill(COLORS["background"])

        self.draw_text_center("Reaktionsspiel Prototyp", self.font_title, COLORS["text"], 120)
        self.draw_text_center("SPACE = Spiel starten", self.font_medium, COLORS["accent"], 240)
        self.draw_text_center("ESC = Beenden", self.font_small, COLORS["subtle"], 290)

        info_lines = [
            f"Aktive Standorte: {len(self.all_locations)}",
            "Tastatur-Simulation:",
            "H = korrekter Treffer",
            "S = Standort ueberspringen",
        ]

        y = 380
        for line in info_lines:
            self.draw_text_center(line, self.font_small, COLORS["subtle"], y)
            y += 34

    def draw_countdown(self):
        self.screen.fill(COLORS["background"])

        elapsed = time.time() - self.countdown_start_time
        remaining = COUNTDOWN_SECONDS - int(elapsed)

        if elapsed >= COUNTDOWN_SECONDS:
            self.start_playing()
            return

        self.draw_text_center("Bereit machen", self.font_title, COLORS["text"], 140)
        self.draw_text_center(str(remaining), self.font_large, COLORS["accent"], self.height // 2)

    def draw_playing(self):
        self.screen.fill(COLORS["background"])

        remaining = int(self.remaining_time())
        if remaining <= 0:
            self.finish_game()
            return

        left_x = 60
        right_x = int(self.width * 0.55)
        top_y = 40

        pygame.draw.rect(
            self.screen,
            COLORS["panel"],
            pygame.Rect(30, 30, self.width - 60, self.height - 60),
            border_radius=18,
        )

        # Header / Status
        self.draw_text_center(f"Zeit: {remaining}s", self.font_medium, COLORS["text"], 60)
        self.draw_text_center(f"Punkte: {self.score}", self.font_medium, COLORS["text"], 105)

        if self.current_location is None:
            self.draw_text_center("Keine weiteren Standorte", self.font_title, COLORS["text"], self.height // 2)
            return

        loc_type = self.current_location.get("type", "unknown")
        type_color = get_type_color(loc_type)

        type_label = get_type_label(loc_type)
        button_id = self.current_location.get("button_id", "-")
        location_id = self.current_location.get("location_id", "-")

        pygame.draw.rect(
            self.screen,
            type_color,
            pygame.Rect(left_x, top_y + 110, int(self.width * 0.42), 8),
            border_radius=4,
        )

        self.draw_wrapped_text(
            self.current_location.get("name", "Unbekannter Standort"),
            self.font_title,
            COLORS["text"],
            left_x,
            top_y + 140,
            int(self.width * 0.42),
        )

        self.draw_wrapped_text(
            f"Typ: {type_label}",
            self.font_medium,
            type_color,
            left_x,
            top_y + 300,
            int(self.width * 0.42),
        )

        self.draw_wrapped_text(
            f"Button-ID: {button_id}",
            self.font_medium,
            COLORS["subtle"],
            left_x,
            top_y + 350,
            int(self.width * 0.42),
        )

        self.draw_wrapped_text(
            f"Location-ID: {location_id}",
            self.font_small,
            COLORS["subtle"],
            left_x,
            top_y + 400,
            int(self.width * 0.42),
        )

        self.draw_wrapped_text(
            self.message,
            self.font_small,
            COLORS["accent"],
            left_x,
            self.height - 120,
            int(self.width * 0.42),
        )

        # Bildbereich
        image_area = pygame.Rect(
            right_x,
            top_y + 120,
            int(self.width * 0.35),
            int(self.height * 0.58),
        )

        pygame.draw.rect(self.screen, (40, 40, 50), image_area, border_radius=12)

        if self.current_image is not None:
            image_rect = self.current_image.get_rect(center=image_area.center)
            self.screen.blit(self.current_image, image_rect)
        else:
            placeholder_font = pygame.font.SysFont("Arial", 28, bold=False)
            placeholder = placeholder_font.render("Kein Bild gefunden", True, COLORS["subtle"])
            placeholder_rect = placeholder.get_rect(center=image_area.center)
            self.screen.blit(placeholder, placeholder_rect)

        # Hilfe unten
        help_text = "H = Treffer | S = Ueberspringen | ESC = Beenden"
        self.draw_text_center(help_text, self.font_small, COLORS["subtle"], self.height - 50)

    def draw_game_over(self):
        self.screen.fill(COLORS["background"])

        self.draw_text_center("Zeit vorbei", self.font_title, COLORS["text"], 150)
        self.draw_text_center(f"Score: {self.score}", self.font_large, COLORS["accent"], 320)
        self.draw_text_center("R = zurueck ins Menue", self.font_medium, COLORS["subtle"], 470)
        self.draw_text_center("ESC = Beenden", self.font_small, COLORS["subtle"], 520)

    def draw(self):
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "countdown":
            self.draw_countdown()
        elif self.state == "playing":
            self.draw_playing()
        elif self.state == "game_over":
            self.draw_game_over()

        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                    if self.state == "menu":
                        if event.key == pygame.K_SPACE:
                            self.start_countdown()

                    elif self.state == "playing":
                        if event.key == pygame.K_h:
                            self.handle_hit()
                        elif event.key == pygame.K_s:
                            self.handle_skip()

                    elif self.state == "game_over":
                        if event.key == pygame.K_r:
                            self.state = "menu"

            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    except Exception as e:
        pygame.quit()
        print("Fehler beim Starten des Spiels:")
        print(e)
        sys.exit(1)
