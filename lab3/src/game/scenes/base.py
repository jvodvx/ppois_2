"""Scene base classes and shared screen styling."""

from __future__ import annotations

import pygame

from ..core import draw_arcade_background, draw_ghost_shape, draw_pacman_shape, load_font


class Scene:
    def __init__(self, app: "PacmanApp"):
        self.app = app

    def on_enter(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        raise NotImplementedError


class BaseScreen(Scene):
    def __init__(self, app: "PacmanApp"):
        super().__init__(app)
        title_candidates = ["Showcard Gothic", "Impact", "Arial Black", "Comic Sans MS"]
        ui_candidates = ["Segoe UI", "Arial", "Verdana", "Tahoma", "Trebuchet MS"]
        self.title_font = load_font(96, bold=True, candidates=title_candidates)
        self.heading_font = load_font(48, bold=True, candidates=ui_candidates)
        self.body_font = load_font(30, bold=True, candidates=ui_candidates)
        self.small_font = load_font(22, candidates=ui_candidates)

    def draw_background(self, surface: pygame.Surface) -> None:
        draw_arcade_background(
            surface,
            background=self.app.colors["background"],
            border=self.app.colors["pacman"],
        )

    def draw_logo(self, surface: pygame.Surface, top: int) -> None:
        letters = [("P", -12), ("A", 10), ("M", -8), ("A", 9), ("N", -6)]
        parts: list[pygame.Surface] = []
        for char, rotation in letters:
            glyph = self.title_font.render(char, True, self.app.colors["text"])
            parts.append(pygame.transform.rotate(glyph, rotation))
        pacman_size = 94
        total_width = sum(part.get_width() for part in parts) + pacman_size - 30
        x = surface.get_width() // 2 - total_width // 2
        for index, part in enumerate(parts):
            rect = part.get_rect(midtop=(x + part.get_width() // 2, top))
            surface.blit(part, rect)
            x += part.get_width() - 8
            if index == 1:
                draw_pacman_shape(surface, (x + pacman_size // 2, top + 52), pacman_size // 2, self.app.colors["pacman"])
                x += pacman_size - 22

    def draw_character_banner(self, surface: pygame.Surface, top: int) -> None:
        width = surface.get_width()
        start_x = width // 2 - 170
        draw_ghost_shape(surface, (start_x, top), 42, self.app.colors["ghosts"]["chaser"])
        draw_ghost_shape(surface, (start_x + 60, top), 42, self.app.colors["ghosts"]["patrol"])
        draw_pacman_shape(surface, (start_x + 160, top), 28, self.app.colors["pacman"])
        pygame.draw.circle(surface, self.app.colors["pellet"], (width // 2 + 185, top), 7)

    def draw_footer_hint(self, surface: pygame.Surface, text: str) -> None:
        hint = self.small_font.render(text, True, pygame.Color("#BFBFBF"))
        rect = hint.get_rect(center=(surface.get_width() // 2, surface.get_height() - 42))
        surface.blit(hint, rect)
