"""Shared constants and drawing helpers."""

from __future__ import annotations

import json
import math
from pathlib import Path

import pygame

ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT_DIR / "config"
DATA_DIR = ROOT_DIR / "data"
LEVELS_DIR = CONFIG_DIR / "levels"

DIRECTION_VECTORS: dict[str, tuple[int, int]] = {
    "left": (-1, 0),
    "right": (1, 0),
    "up": (0, -1),
    "down": (0, 1),
}
DIR_SEQUENCE = [
    DIRECTION_VECTORS["left"],
    DIRECTION_VECTORS["up"],
    DIRECTION_VECTORS["right"],
    DIRECTION_VECTORS["down"],
]
ZERO_DIR = (0, 0)


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as file:
        return json.load(file)


def save_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def hex_color(value: str) -> pygame.Color:
    return pygame.Color(value)


def load_font(
    size: int,
    *,
    bold: bool = False,
    italic: bool = False,
    candidates: list[str] | None = None,
) -> pygame.font.Font:
    candidates = candidates or [
        "Showcard Gothic",
        "Impact",
        "Arial Black",
        "Comic Sans MS",
        "Trebuchet MS",
        "Segoe UI",
    ]
    for name in candidates:
        path = pygame.font.match_font(name, bold=bold, italic=italic)
        if path:
            return pygame.font.Font(path, size)
    return pygame.font.SysFont(None, size, bold=bold, italic=italic)


def fit_text_font(
    text: str,
    max_width: int,
    start_size: int,
    *,
    bold: bool = True,
    candidates: list[str] | None = None,
) -> pygame.font.Font:
    size = start_size
    while size >= 18:
        font = load_font(size, bold=bold, candidates=candidates)
        if font.size(text)[0] <= max_width:
            return font
        size -= 2
    return load_font(18, bold=bold, candidates=candidates)


def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if font.size(candidate)[0] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def reverse_direction(direction: tuple[int, int]) -> tuple[int, int]:
    return (-direction[0], -direction[1])


def cell_center(cell: tuple[int, int]) -> pygame.Vector2:
    return pygame.Vector2(cell[0] + 0.5, cell[1] + 0.5)


def direction_angle(direction: tuple[int, int]) -> float:
    if direction == DIRECTION_VECTORS["left"]:
        return 180.0
    if direction == DIRECTION_VECTORS["up"]:
        return 270.0
    if direction == DIRECTION_VECTORS["down"]:
        return 90.0
    return 0.0


def draw_pacman_shape(
    surface: pygame.Surface,
    center: tuple[int, int],
    radius: int,
    color: pygame.Color,
    *,
    facing: tuple[int, int] = DIRECTION_VECTORS["right"],
) -> None:
    mouth = 42
    angle = direction_angle(facing)
    points = [center]
    start_angle = math.radians(angle + mouth / 2)
    end_angle = math.radians(angle + 360 - mouth / 2)
    for step in range(37):
        current = start_angle + (end_angle - start_angle) * step / 36
        points.append(
            (
                center[0] + int(math.cos(current) * radius),
                center[1] + int(math.sin(current) * radius),
            )
        )
    pygame.draw.polygon(surface, color, points)
    eye = (center[0] + int(radius * 0.10), center[1] - int(radius * 0.55))
    pygame.draw.circle(surface, pygame.Color("#111111"), eye, max(2, radius // 8))


def draw_ghost_shape(
    surface: pygame.Surface,
    center: tuple[int, int],
    size: int,
    color: pygame.Color,
) -> None:
    width = size
    height = int(size * 1.15)
    ghost_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    body_top = int(height * 0.20)
    eye_y = int(height * 0.56)
    bottom = height - 2
    pygame.draw.ellipse(ghost_surface, color, (0, 0, width, int(height * 0.74)))
    pygame.draw.rect(ghost_surface, color, (0, body_top, width, int(height * 0.46)))
    body_points = [
        (0, body_top),
        (0, bottom),
        (int(width * 0.16), int(height * 0.82)),
        (int(width * 0.32), bottom),
        (int(width * 0.50), int(height * 0.82)),
        (int(width * 0.68), bottom),
        (int(width * 0.84), int(height * 0.82)),
        (width, bottom),
        (width, body_top),
    ]
    pygame.draw.polygon(ghost_surface, color, body_points)
    eye_radius = max(4, size // 8)
    pupil_radius = max(2, size // 16)
    for eye_center in ((int(width * 0.34), eye_y), (int(width * 0.66), eye_y)):
        pygame.draw.circle(ghost_surface, pygame.Color("#F9F9F9"), eye_center, eye_radius + 2)
        pygame.draw.circle(
            ghost_surface,
            pygame.Color("#1B7CFF"),
            (eye_center[0] + pupil_radius, eye_center[1]),
            pupil_radius,
        )
    surface.blit(ghost_surface, ghost_surface.get_rect(center=center))


def draw_freeze_power(surface: pygame.Surface, center: tuple[int, int], size: int) -> None:
    color = pygame.Color("#7EE7FF")
    outline = pygame.Color("#DFFFFF")
    radius = max(6, size // 3)
    pygame.draw.circle(surface, outline, center, radius + 2)
    pygame.draw.circle(surface, color, center, radius)
    for dx, dy in ((0, -radius), (0, radius), (-radius, 0), (radius, 0)):
        pygame.draw.line(surface, outline, center, (center[0] + dx, center[1] + dy), 2)


def draw_speed_power(surface: pygame.Surface, center: tuple[int, int], size: int) -> None:
    color = pygame.Color("#FFA93A")
    outline = pygame.Color("#FFF1B7")
    radius = max(7, size // 3)
    points = [
        (center[0] - radius // 2, center[1] - radius),
        (center[0] + radius // 3, center[1] - radius // 3),
        (center[0], center[1] - radius // 3),
        (center[0] + radius // 2, center[1] + radius),
        (center[0] - radius // 3, center[1] + radius // 4),
        (center[0], center[1] + radius // 4),
    ]
    pygame.draw.polygon(surface, outline, points)
    pygame.draw.polygon(surface, color, points, 0)


def draw_arcade_background(
    surface: pygame.Surface,
    *,
    background: pygame.Color,
    border: pygame.Color,
) -> None:
    surface.fill(background)
    width, height = surface.get_size()
    for stripe in range(0, width + height, 54):
        pygame.draw.line(surface, pygame.Color("#0B0B2C"), (stripe, 0), (0, stripe), 1)
    for index in range(7):
        radius = 180 + index * 42
        alpha = max(60 - index * 7, 14)
        glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (18, 18, 75, alpha), (radius, radius), radius, width=3)
        surface.blit(glow, glow.get_rect(center=(width // 2, height // 2 - 120)))
    frame = pygame.Rect(18, 18, width - 36, height - 36)
    pygame.draw.rect(surface, border, frame, width=2, border_radius=12)
