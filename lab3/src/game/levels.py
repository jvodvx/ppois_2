"""Level metadata and map parsing."""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from .core import LEVELS_DIR, load_json


@dataclass(frozen=True)
class LevelSpec:
    number: int
    map_name: str
    label: str
    player_speed: float
    red_speed: float
    blue_speed: float
    release_delays: tuple[float, float, float, float]
    freeze_duration: float
    boost_duration: float
    boost_multiplier: float
    patrol_routes: tuple[tuple[tuple[int, int], ...], tuple[tuple[int, int], ...]]


@dataclass(frozen=True)
class CampaignSpec:
    key: str
    title: str
    subtitle: str
    level_indices: tuple[int, ...]


LEVEL_SPECS = [
    LevelSpec(1, "level1.json", "Classic Warmup", 4.3, 3.1, 2.7, (0.0, 7.0, 13.0, 18.0), 4.8, 6.0, 1.35, (((4, 4), (8, 4), (8, 7), (4, 7)), ((20, 4), (16, 4), (16, 7), (20, 7)))),
    LevelSpec(2, "level1.json", "Classic Pressure", 4.5, 3.45, 3.0, (0.0, 5.5, 10.0, 14.5), 4.2, 5.4, 1.30, (((4, 4), (8, 4), (8, 7), (4, 7)), ((20, 4), (16, 4), (16, 7), (20, 7)))),
    LevelSpec(3, "level2.json", "Advanced Shift", 4.6, 3.7, 3.2, (0.0, 4.8, 8.4, 12.0), 3.8, 5.0, 1.28, (((3, 5), (7, 5), (7, 8), (3, 8)), ((21, 14), (17, 14), (17, 17), (21, 17)))),
    LevelSpec(4, "level2.json", "Advanced Finale", 4.8, 3.95, 3.45, (0.0, 3.8, 6.8, 9.8), 3.2, 4.4, 1.25, (((3, 5), (7, 5), (7, 8), (3, 8)), ((21, 14), (17, 14), (17, 17), (21, 17)))),
]

CAMPAIGNS = {
    "classic": CampaignSpec("classic", "CLASSIC MAP", "Easier, levels 1-2", (0, 1)),
    "advanced": CampaignSpec("advanced", "ADVANCED MAP", "Harder, levels 3-4", (2, 3)),
}


class GameMap:
    def __init__(self, data: dict):
        self.name = data.get("name", "Level")
        self.layout = data["layout"]
        self.rows = len(self.layout)
        self.cols = max(len(row) for row in self.layout)
        self.walls: set[tuple[int, int]] = set()
        self.walkable: set[tuple[int, int]] = set()
        self.freeze_pellets: set[tuple[int, int]] = set()
        self.speed_pellets: set[tuple[int, int]] = set()
        self.base_pellets: set[tuple[int, int]] = set()
        self.player_spawn = (1, 1)
        self.ghost_anchors: list[tuple[int, int]] = []
        self.house_cells: set[tuple[int, int]] = set()
        self.house_bounds = pygame.Rect(0, 0, 0, 0)
        self.door: tuple[int, int] | None = None

        for row_index, row in enumerate(self.layout):
            for col_index, marker in enumerate(row):
                cell = (col_index, row_index)
                if marker == "#":
                    self.walls.add(cell)
                    continue
                self.walkable.add(cell)
                if marker == ".":
                    self.base_pellets.add(cell)
                elif marker == "P":
                    self.player_spawn = cell
                elif marker == "E":
                    self.ghost_anchors.append(cell)
                elif marker == "F":
                    self.freeze_pellets.add(cell)
                elif marker == "S":
                    self.speed_pellets.add(cell)
                elif marker == "D":
                    self.door = cell

        self._infer_house()
        if not self.ghost_anchors:
            self.ghost_anchors = [self.player_spawn, self.player_spawn]
        if len(self.ghost_anchors) == 1:
            self.ghost_anchors.append(self.ghost_anchors[0])

    def _infer_house(self) -> None:
        if not self.ghost_anchors:
            return
        xs = [cell[0] for cell in self.ghost_anchors]
        ys = [cell[1] for cell in self.ghost_anchors]
        left = max(min(xs) - 1, 0)
        right = min(max(xs) + 1, self.cols - 1)
        top = min(ys)
        bottom = min(max(ys) + 1, self.rows - 1)
        self.house_cells = {
            (x, y)
            for y in range(top, bottom + 1)
            for x in range(left, right + 1)
            if (x, y) in self.walkable
        }
        if self.door is None:
            candidate_y = top - 1
            center_x = round(sum(xs) / len(xs))
            self.door = (center_x, max(candidate_y, 0))
            self.walkable.add(self.door)
        else:
            self.walkable.add(self.door)
        self.house_bounds = pygame.Rect(left, top, right - left + 1, bottom - top + 1)

    def in_bounds(self, cell: tuple[int, int]) -> bool:
        return 0 <= cell[0] < self.cols and 0 <= cell[1] < self.rows

    def player_walkable(self, cell: tuple[int, int]) -> bool:
        if cell in self.walls or not self.in_bounds(cell):
            return False
        if self.door is not None and cell == self.door:
            return False
        return cell not in self.house_cells

    def ghost_walkable(self, cell: tuple[int, int]) -> bool:
        return self.in_bounds(cell) and cell not in self.walls

    def ghost_spawn_cells(self) -> list[tuple[int, int]]:
        xs = [cell[0] for cell in self.ghost_anchors]
        ys = [cell[1] for cell in self.ghost_anchors]
        left = min(xs)
        right = max(xs)
        top = min(ys)
        bottom = min(self.rows - 1, max(ys) + 1)
        result = [cell for cell in [(left, top), (right, top), (left, bottom), (right, bottom)] if cell in self.walkable]
        while len(result) < 4:
            result.append(result[-1])
        return result[:4]


def load_map(name: str) -> GameMap:
    return GameMap(load_json(LEVELS_DIR / name))
