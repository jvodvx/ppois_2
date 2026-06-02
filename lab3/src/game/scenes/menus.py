"""Menu-like scenes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import pygame

from ..core import draw_pacman_shape, wrap_text, fit_text_font, load_font
from ..levels import CAMPAIGNS
from .base import BaseScreen


@dataclass
class MenuOption:
    label: str
    action: Callable[[], None]
    subtitle: str = ""
    rect: pygame.Rect = field(default_factory=lambda: pygame.Rect(0, 0, 0, 0))


class MenuScene(BaseScreen):
    def __init__(self, app: "PacmanApp"):
        super().__init__(app)
        self.button_font = load_font(42, bold=True, candidates=["Segoe UI", "Arial", "Verdana", "Tahoma"])
        self.selected_index = 0
        self.menu_options = [
            MenuOption("START GAME", lambda: self.app.change_scene("map_select"), "Choose a map first"),
            MenuOption("HIGH SCORES", lambda: self.app.change_scene("records")),
            MenuOption("HELP", lambda: self.app.change_scene("help")),
            MenuOption("EXIT", self.app.quit),
        ]

    def on_enter(self) -> None:
        self.app.audio.play_music("menu")

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.menu_options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.menu_options)
            elif event.key == pygame.K_ESCAPE:
                self.app.quit()
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.menu_options[self.selected_index].action()
        elif event.type == pygame.MOUSEMOTION:
            for index, option in enumerate(self.menu_options):
                if option.rect.collidepoint(event.pos):
                    self.selected_index = index
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for option in self.menu_options:
                if option.rect.collidepoint(event.pos):
                    option.action()
                    break

    def draw(self, surface: pygame.Surface) -> None:
        self.draw_background(surface)
        self.draw_logo(surface, 58)
        self.draw_character_banner(surface, 270)
        center_x = surface.get_width() // 2
        start_y = 410
        spacing = 66
        for index, option in enumerate(self.menu_options):
            active = index == self.selected_index
            color = self.app.colors["pacman"] if active else self.app.colors["text"]
            shadow = self.button_font.render(option.label, True, pygame.Color("#171717"))
            text = self.button_font.render(option.label, True, color)
            shadow = pygame.transform.rotate(shadow, -3 if active else 0)
            text = pygame.transform.rotate(text, -3 if active else 0)
            rect = text.get_rect(center=(center_x, start_y + index * spacing))
            option.rect = rect.inflate(36, 18)
            surface.blit(shadow, rect.move(4, 4))
            surface.blit(text, rect)
            if active:
                draw_pacman_shape(surface, (rect.left - 34, rect.centery), 12, self.app.colors["pacman"])
        self.draw_footer_hint(surface, "Enter - select   Esc - exit   F11 - fullscreen")


class MapSelectScene(BaseScreen):
    def __init__(self, app: "PacmanApp"):
        super().__init__(app)
        self.button_font = load_font(36, bold=True, candidates=["Segoe UI", "Arial", "Verdana", "Tahoma"])
        self.selected_index = 0
        self.options = [
            MenuOption(CAMPAIGNS["classic"].title, lambda: self.app.start_new_game("classic"), CAMPAIGNS["classic"].subtitle),
            MenuOption(CAMPAIGNS["advanced"].title, lambda: self.app.start_new_game("advanced"), CAMPAIGNS["advanced"].subtitle),
            MenuOption("BACK", lambda: self.app.change_scene("menu")),
        ]

    def on_enter(self) -> None:
        self.app.audio.play_music("menu")

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key == pygame.K_ESCAPE:
                self.app.change_scene("menu")
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.options[self.selected_index].action()
        elif event.type == pygame.MOUSEMOTION:
            for index, option in enumerate(self.options):
                if option.rect.collidepoint(event.pos):
                    self.selected_index = index
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for option in self.options:
                if option.rect.collidepoint(event.pos):
                    option.action()
                    break

    def draw(self, surface: pygame.Surface) -> None:
        self.draw_background(surface)
        self.draw_logo(surface, 36)
        heading = self.heading_font.render("CHOOSE MAP", True, self.app.colors["text"])
        surface.blit(heading, heading.get_rect(center=(surface.get_width() // 2, 205)))
        panel = pygame.Rect(120, 250, surface.get_width() - 240, 330)
        pygame.draw.rect(surface, pygame.Color("#060612"), panel, border_radius=18)
        pygame.draw.rect(surface, self.app.colors["wall"], panel, width=3, border_radius=18)
        y = panel.top + 56
        for index, option in enumerate(self.options):
            active = index == self.selected_index
            color = self.app.colors["pacman"] if active else self.app.colors["text"]
            text = self.button_font.render(option.label, True, color)
            subtitle = self.small_font.render(option.subtitle, True, pygame.Color("#BFBFBF")) if option.subtitle else None
            rect = pygame.Rect(panel.left + 36, y - 24, panel.width - 72, 72)
            option.rect = rect
            if active:
                pygame.draw.rect(surface, pygame.Color("#13133A"), rect, border_radius=14)
                pygame.draw.rect(surface, self.app.colors["wall"], rect, width=2, border_radius=14)
            surface.blit(text, text.get_rect(midleft=(rect.left + 18, rect.centery - 10)))
            if subtitle is not None:
                surface.blit(subtitle, subtitle.get_rect(midleft=(rect.left + 18, rect.centery + 16)))
            y += 90
        self.draw_footer_hint(surface, "Enter - select   Esc - back")


class HelpScene(BaseScreen):
    def __init__(self, app: "PacmanApp"):
        super().__init__(app)
        self.lines = [
            "Collect every small pellet to clear the level.",
            "Pac-Man has 3 lives. A ghost collision resets positions but keeps pellet progress.",
            "Two large cyan power-ups freeze active ghosts. Two orange power-ups speed up Pac-Man.",
            "Only one red ghost starts outside the ghost house. The other three are released over time.",
            "Red ghosts chase Pac-Man. Blue ghosts patrol fixed sectors of the map.",
            "Pick a map in the start menu: classic is easier, advanced is harder.",
        ]

    def on_enter(self) -> None:
        self.app.audio.play_music("menu")

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
            self.app.change_scene("menu")
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.app.change_scene("menu")

    def draw(self, surface: pygame.Surface) -> None:
        self.draw_background(surface)
        self.draw_logo(surface, 36)
        heading = self.heading_font.render("HELP", True, self.app.colors["text"])
        surface.blit(heading, heading.get_rect(center=(surface.get_width() // 2, 205)))
        panel = pygame.Rect(80, 240, surface.get_width() - 160, 390)
        pygame.draw.rect(surface, pygame.Color("#060612"), panel, border_radius=18)
        pygame.draw.rect(surface, self.app.colors["wall"], panel, width=3, border_radius=18)
        y = panel.top + 28
        for line in self.lines:
            for wrapped in wrap_text(line, self.small_font, panel.width - 48):
                text = self.small_font.render(wrapped, True, self.app.colors["text"])
                surface.blit(text, (panel.left + 24, y))
                y += 32
            y += 8
        self.draw_footer_hint(surface, "Esc or click - back to menu")


class RecordsScene(BaseScreen):
    def __init__(self, app: "PacmanApp"):
        super().__init__(app)
        self.records: list[dict] = []

    def on_enter(self) -> None:
        self.app.audio.play_music("menu")
        self.records = self.app.load_records()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
            self.app.change_scene("menu")
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.app.change_scene("menu")

    def draw(self, surface: pygame.Surface) -> None:
        self.draw_background(surface)
        self.draw_logo(surface, 36)
        heading = self.heading_font.render("HIGH SCORES", True, self.app.colors["text"])
        surface.blit(heading, heading.get_rect(center=(surface.get_width() // 2, 205)))
        panel = pygame.Rect(140, 255, surface.get_width() - 280, 300)
        pygame.draw.rect(surface, pygame.Color("#060612"), panel, border_radius=18)
        pygame.draw.rect(surface, self.app.colors["wall"], panel, width=3, border_radius=18)
        if not self.records:
            empty = self.body_font.render("No saved runs yet", True, self.app.colors["text"])
            surface.blit(empty, empty.get_rect(center=panel.center))
        else:
            y = panel.top + 48
            for index, record in enumerate(self.records[:3], start=1):
                line = f"{index}. {record['name']}  {record['score']} pts"
                font = fit_text_font(line, panel.width - 60, 30, candidates=["Segoe UI", "Arial", "Verdana", "Tahoma"])
                text = font.render(line, True, self.app.colors["text"])
                surface.blit(text, text.get_rect(center=(panel.centerx, y)))
                y += 72
        self.draw_footer_hint(surface, "Esc or click - back to menu")
