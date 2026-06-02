"""Gameplay scene."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import pygame

from .core import (
    DIR_SEQUENCE,
    DIRECTION_VECTORS,
    ZERO_DIR,
    cell_center,
    draw_arcade_background,
    draw_freeze_power,
    draw_ghost_shape,
    draw_pacman_shape,
    draw_speed_power,
    fit_text_font,
    load_font,
    reverse_direction,
)
from .levels import CAMPAIGNS, LEVEL_SPECS, GameMap
from .scenes.base import Scene


@dataclass
class GhostState:
    name: str
    role: str
    color_key: str
    spawn_cell: tuple[int, int]
    patrol_route: tuple[tuple[int, int], ...]
    release_delay: float
    position: pygame.Vector2 = field(default_factory=pygame.Vector2)
    current_direction: tuple[int, int] = ZERO_DIR
    active: bool = False
    route_index: int = 0
    has_left_house: bool = False

    def reset(self) -> None:
        self.position = cell_center(self.spawn_cell)
        self.current_direction = ZERO_DIR
        self.active = self.release_delay <= 0
        self.route_index = 0
        self.has_left_house = False


class GameScene(Scene):
    def __init__(self, app: "PacmanApp"):
        super().__init__(app)
        ui_candidates = ["Segoe UI", "Arial", "Verdana", "Tahoma"]
        self.header_font = load_font(30, bold=True, candidates=ui_candidates)
        self.body_font = load_font(22, candidates=ui_candidates)
        self.small_font = load_font(18, candidates=ui_candidates)
        self.overlay_font = load_font(44, bold=True, candidates=ui_candidates)
        self.level_specs = LEVEL_SPECS
        self.campaign = CAMPAIGNS["classic"]
        self.current_level_pos = 0
        self.current_spec = self.level_specs[self.campaign.level_indices[self.current_level_pos]]
        self.map = self.app.get_map(self.current_spec.map_name)
        self.score = 0
        self.lives = 3
        self.level_time = 0.0
        self.freeze_timer = 0.0
        self.boost_timer = 0.0
        self.player_position = cell_center(self.map.player_spawn)
        self.player_direction = ZERO_DIR
        self.player_desired_direction = ZERO_DIR
        self.player_facing = DIRECTION_VECTORS["right"]
        self.pellets: set[tuple[int, int]] = set()
        self.freeze_pellets: set[tuple[int, int]] = set()
        self.speed_pellets: set[tuple[int, int]] = set()
        self.ghosts: list[GhostState] = []
        self.phase = "intro"
        self.phase_timer = 0.0
        self.banner_text = ""
        self.end_target_scene = "menu"
        self.record_saved = False

    def on_enter(self) -> None:
        self.app.audio.play_music("gameplay")

    def start_new_game(self, campaign_key: str) -> None:
        self.campaign = CAMPAIGNS[campaign_key]
        self.current_level_pos = 0
        self.score = 0
        self.lives = 3
        self.record_saved = False
        self.load_level(reset_lives=True)

    def load_level(self, *, reset_lives: bool) -> None:
        self.current_spec = self.level_specs[self.campaign.level_indices[self.current_level_pos]]
        self.map = self.app.get_map(self.current_spec.map_name)
        self.pellets = set(self.map.base_pellets)
        self.freeze_pellets = set(self.map.freeze_pellets)
        self.speed_pellets = set(self.map.speed_pellets)
        self.freeze_timer = 0.0
        self.boost_timer = 0.0
        self.level_time = 0.0
        self.player_facing = DIRECTION_VECTORS["right"]
        if reset_lives:
            self.lives = 3
        self.reset_positions(initial=True)
        self.phase = "intro"
        self.phase_timer = 1.4
        self.banner_text = f"LEVEL {self.current_spec.number}  {self.current_spec.label}"

    def reset_positions(self, *, initial: bool = False) -> None:
        self.player_position = cell_center(self.map.player_spawn)
        self.player_direction = ZERO_DIR
        self.player_desired_direction = ZERO_DIR
        spawn_cells = self.map.ghost_spawn_cells()
        patrol_routes = self.current_spec.patrol_routes
        self.ghosts = [
            GhostState("Red Alpha", "chaser", "chaser", spawn_cells[0], tuple(), self.current_spec.release_delays[0]),
            GhostState("Red Beta", "chaser", "chaser", spawn_cells[1], tuple(), self.current_spec.release_delays[1]),
            GhostState("Blue Orbit", "patrol", "patrol", spawn_cells[2], patrol_routes[0], self.current_spec.release_delays[2]),
            GhostState("Blue Loop", "patrol", "patrol", spawn_cells[3], patrol_routes[1], self.current_spec.release_delays[3]),
        ]
        for ghost in self.ghosts:
            ghost.reset()
        if not initial:
            self.freeze_timer = 0.0
            self.boost_timer = 0.0
            self.level_time = 0.0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_ESCAPE:
            self.app.change_scene("menu")
            return
        if event.key in (pygame.K_LEFT, pygame.K_a):
            self.player_desired_direction = DIRECTION_VECTORS["left"]
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.player_desired_direction = DIRECTION_VECTORS["right"]
        elif event.key in (pygame.K_UP, pygame.K_w):
            self.player_desired_direction = DIRECTION_VECTORS["up"]
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.player_desired_direction = DIRECTION_VECTORS["down"]

    def update(self, dt: float) -> None:
        if self.phase in {"game_over", "campaign_win"}:
            self.phase_timer -= dt
            if self.phase_timer <= 0:
                self.app.change_scene(self.end_target_scene)
            return
        if self.phase == "level_clear":
            self.phase_timer -= dt
            if self.phase_timer <= 0:
                self.advance_to_next_level()
            return
        if self.phase in {"intro", "respawn"}:
            self.phase_timer -= dt
            if self.phase_timer <= 0:
                self.phase = "playing"
                self.banner_text = ""
            return

        self.level_time += dt
        if self.freeze_timer > 0:
            self.freeze_timer = max(0.0, self.freeze_timer - dt)
        if self.boost_timer > 0:
            self.boost_timer = max(0.0, self.boost_timer - dt)
        self.activate_waiting_ghosts()
        self.update_player(dt)
        self.collect_pickups()
        self.update_ghosts(dt)
        self.check_collisions()
        if not self.pellets and not self.freeze_pellets and not self.speed_pellets:
            self.score += 200 * self.current_spec.number
            self.app.audio.play_sfx("win")
            self.phase = "level_clear"
            self.phase_timer = 1.5
            self.banner_text = f"LEVEL {self.current_spec.number} CLEAR"

    def activate_waiting_ghosts(self) -> None:
        for ghost in self.ghosts:
            if not ghost.active and self.level_time >= ghost.release_delay:
                ghost.active = True

    def update_player(self, dt: float) -> None:
        speed = self.current_spec.player_speed * (self.current_spec.boost_multiplier if self.boost_timer > 0 else 1.0)
        self.player_position, self.player_direction = self.move_actor(
            position=self.player_position,
            current_direction=self.player_direction,
            desired_direction=self.player_desired_direction,
            speed=speed,
            dt=dt,
            player=True,
        )
        if self.player_direction != ZERO_DIR:
            self.player_facing = self.player_direction

    def update_ghosts(self, dt: float) -> None:
        if self.freeze_timer > 0:
            return
        player_cell = self.cell_from_position(self.player_position)
        for ghost in self.ghosts:
            if not ghost.active:
                continue
            ghost_speed = self.current_spec.red_speed if ghost.role == "chaser" else self.current_spec.blue_speed
            if self.is_centered(ghost.position):
                current_cell = self.cell_from_position(ghost.position)
                ghost.position = cell_center(current_cell)
                if current_cell not in self.map.house_cells and current_cell != self.map.door:
                    ghost.has_left_house = True
                target = self.resolve_ghost_target(ghost, current_cell, player_cell)
                ghost.current_direction = self.choose_direction(current_cell, ghost.current_direction, target)
            ghost.position, ghost.current_direction = self.move_actor(
                position=ghost.position,
                current_direction=ghost.current_direction,
                desired_direction=ghost.current_direction,
                speed=ghost_speed,
                dt=dt,
                player=False,
            )

    def resolve_ghost_target(self, ghost: GhostState, current_cell: tuple[int, int], player_cell: tuple[int, int]) -> tuple[int, int]:
        if not ghost.has_left_house:
            if current_cell in self.map.house_cells and self.map.door is not None:
                if current_cell[0] != self.map.door[0]:
                    return (self.map.door[0], current_cell[1])
                return self.map.door
            if self.map.door is not None and current_cell == self.map.door:
                return (self.map.door[0], self.map.door[1] - 1)
            ghost.has_left_house = True
        if ghost.role == "chaser":
            return player_cell
        target = ghost.patrol_route[ghost.route_index % len(ghost.patrol_route)] if ghost.patrol_route else player_cell
        if ghost.patrol_route and current_cell == target:
            ghost.route_index = (ghost.route_index + 1) % len(ghost.patrol_route)
            target = ghost.patrol_route[ghost.route_index]
        return target

    def move_actor(self, *, position: pygame.Vector2, current_direction: tuple[int, int], desired_direction: tuple[int, int], speed: float, dt: float, player: bool) -> tuple[pygame.Vector2, tuple[int, int]]:
        pos = position.copy()
        cell = self.cell_from_position(pos)
        if self.is_centered(pos):
            pos = cell_center(cell)
            if desired_direction != ZERO_DIR and self.can_move(cell, desired_direction, player=player):
                current_direction = desired_direction
            if current_direction != ZERO_DIR and not self.can_move(cell, current_direction, player=player):
                current_direction = ZERO_DIR
        if current_direction == ZERO_DIR:
            return pos, current_direction
        target_cell = self.next_target_cell(pos, current_direction)
        if not self.is_transition_allowed(target_cell, player=player):
            return cell_center(self.cell_from_position(pos)), ZERO_DIR
        target = cell_center(target_cell)
        distance = speed * dt
        delta = target - pos
        if current_direction[0] != 0:
            pos.x += math.copysign(min(abs(delta.x), distance), current_direction[0])
            pos.y = round(target.y, 4)
        else:
            pos.y += math.copysign(min(abs(delta.y), distance), current_direction[1])
            pos.x = round(target.x, 4)
        if pos.distance_to(target) <= 0.001:
            pos = target
        return pos, current_direction

    def next_target_cell(self, position: pygame.Vector2, direction: tuple[int, int]) -> tuple[int, int]:
        if direction[0] > 0:
            return (math.floor(position.x - 0.5) + 1, int(round(position.y - 0.5)))
        if direction[0] < 0:
            return (math.ceil(position.x - 0.5) - 1, int(round(position.y - 0.5)))
        if direction[1] > 0:
            return (int(round(position.x - 0.5)), math.floor(position.y - 0.5) + 1)
        return (int(round(position.x - 0.5)), math.ceil(position.y - 0.5) - 1)

    def is_transition_allowed(self, cell: tuple[int, int], *, player: bool) -> bool:
        return self.map.player_walkable(cell) if player else self.map.ghost_walkable(cell)

    def choose_direction(self, cell: tuple[int, int], current_direction: tuple[int, int], target: tuple[int, int]) -> tuple[int, int]:
        valid = [direction for direction in DIR_SEQUENCE if self.can_move(cell, direction, player=False)]
        if not valid:
            return ZERO_DIR
        reverse = reverse_direction(current_direction)
        if len(valid) > 1 and reverse in valid:
            valid.remove(reverse)
        def score(direction: tuple[int, int]) -> tuple[float, float]:
            next_cell = (cell[0] + direction[0], cell[1] + direction[1])
            distance = (next_cell[0] - target[0]) ** 2 + (next_cell[1] - target[1]) ** 2
            return distance, 0.0 if direction == current_direction else 0.2
        return min(valid, key=score)

    def can_move(self, cell: tuple[int, int], direction: tuple[int, int], *, player: bool) -> bool:
        next_cell = (cell[0] + direction[0], cell[1] + direction[1])
        return self.map.player_walkable(next_cell) if player else self.map.ghost_walkable(next_cell)

    def collect_pickups(self) -> None:
        if not self.is_centered(self.player_position):
            return
        cell = self.cell_from_position(self.player_position)
        if cell in self.pellets:
            self.pellets.remove(cell)
            self.score += 10
            self.app.audio.play_sfx("pellet")
        elif cell in self.freeze_pellets:
            self.freeze_pellets.remove(cell)
            self.freeze_timer = self.current_spec.freeze_duration
            self.score += 50
            self.app.audio.play_sfx("pellet")
        elif cell in self.speed_pellets:
            self.speed_pellets.remove(cell)
            self.boost_timer = self.current_spec.boost_duration
            self.score += 50
            self.app.audio.play_sfx("pellet")

    def check_collisions(self) -> None:
        for ghost in self.ghosts:
            if ghost.active and ghost.position.distance_to(self.player_position) <= 0.46:
                self.handle_hit()
                return

    def handle_hit(self) -> None:
        if self.lives > 1:
            self.lives -= 1
            self.app.audio.play_sfx("death")
            self.reset_positions(initial=False)
            self.phase = "respawn"
            self.phase_timer = 1.3
            self.banner_text = "LIFE LOST"
            return
        self.lives = 0
        self.app.audio.play_sfx("lose")
        self.save_record()
        self.phase = "game_over"
        self.phase_timer = 2.6
        self.banner_text = f"GAME OVER  SCORE {self.score}"
        self.end_target_scene = "records"

    def advance_to_next_level(self) -> None:
        if self.current_level_pos < len(self.campaign.level_indices) - 1:
            self.current_level_pos += 1
            self.load_level(reset_lives=True)
            return
        self.score += 500
        self.app.audio.play_sfx("win")
        self.save_record()
        self.phase = "campaign_win"
        self.phase_timer = 3.0
        self.banner_text = f"CAMPAIGN CLEAR  SCORE {self.score}"
        self.end_target_scene = "records"

    def save_record(self) -> None:
        if not self.record_saved:
            self.record_saved = True
            self.app.save_record({"name": "PLAYER", "score": self.score})

    def cell_from_position(self, position: pygame.Vector2) -> tuple[int, int]:
        return (int(position.x), int(position.y))

    def is_centered(self, position: pygame.Vector2) -> bool:
        cell = self.cell_from_position(position)
        return abs(position.x - (cell[0] + 0.5)) < 0.02 and abs(position.y - (cell[1] + 0.5)) < 0.02

    def geometry(self, surface: pygame.Surface) -> tuple[int, int, int]:
        width, height = surface.get_size()
        top_margin = 118
        bottom_margin = 36
        side_margin = 28
        tile = int(min((width - side_margin * 2) / self.map.cols, (height - top_margin - bottom_margin) / self.map.rows))
        tile = max(tile, 18)
        return tile, (width - tile * self.map.cols) // 2, top_margin + (height - top_margin - bottom_margin - tile * self.map.rows) // 2

    def draw(self, surface: pygame.Surface) -> None:
        draw_arcade_background(
            surface,
            background=self.app.colors["background"],
            border=self.app.colors["wall"],
        )
        tile, origin_x, origin_y = self.geometry(surface)
        self.draw_hud(surface)
        self.draw_maze(surface, tile, origin_x, origin_y)
        self.draw_entities(surface, tile, origin_x, origin_y)
        self.draw_overlay(surface)

    def draw_hud(self, surface: pygame.Surface) -> None:
        width = surface.get_width()
        level_label = f"LEVEL {self.current_spec.number}: {self.current_spec.label}"
        level_font = fit_text_font(level_label, width - 320, 30, candidates=["Segoe UI", "Arial", "Verdana", "Tahoma"])
        surface.blit(level_font.render(level_label, True, self.app.colors["text"]), (24, 18))
        surface.blit(self.header_font.render(f"SCORE {self.score}", True, self.app.colors["text"]), (24, 52))
        surface.blit(self.small_font.render("Esc - menu   F11 - fullscreen", True, pygame.Color("#C8C8C8")), (width - 250, 22))
        surface.blit(self.body_font.render("LIVES", True, self.app.colors["text"]), (24, 88))
        for index in range(self.lives):
            draw_pacman_shape(surface, (108 + index * 28, 99), 10, self.app.colors["pacman"])
        effects = []
        if self.freeze_timer > 0:
            effects.append(f"Freeze: {self.freeze_timer:0.1f}s")
        if self.boost_timer > 0:
            effects.append(f"Speed: {self.boost_timer:0.1f}s")
        label = "   ".join(effects) if effects else "No active power-up"
        surface.blit(self.small_font.render(label, True, pygame.Color("#D0D0D0")), (240, 92))

    def draw_maze(self, surface: pygame.Surface, tile: int, origin_x: int, origin_y: int) -> None:
        maze_rect = pygame.Rect(origin_x - 10, origin_y - 10, tile * self.map.cols + 20, tile * self.map.rows + 20)
        pygame.draw.rect(surface, pygame.Color("#020214"), maze_rect, border_radius=18)
        pygame.draw.rect(surface, pygame.Color("#1212A0"), maze_rect, width=2, border_radius=18)
        if self.map.house_bounds.width > 0:
            bounds = self.map.house_bounds
            house_rect = pygame.Rect(origin_x + bounds.x * tile, origin_y + bounds.y * tile, bounds.width * tile, bounds.height * tile).inflate(-tile // 3, -tile // 3)
            pygame.draw.rect(surface, pygame.Color("#151515"), house_rect, border_radius=10)
            pygame.draw.rect(surface, self.app.colors["wall"], house_rect, width=2, border_radius=10)
        for row_index in range(self.map.rows):
            row = self.map.layout[row_index]
            for col_index in range(self.map.cols):
                cell = (col_index, row_index)
                rect = pygame.Rect(origin_x + col_index * tile, origin_y + row_index * tile, tile, tile)
                marker = row[col_index] if col_index < len(row) else "#"
                if marker == "#":
                    self.draw_wall(surface, rect)
                    continue
                center = rect.center
                if cell in self.pellets:
                    pygame.draw.circle(surface, self.app.colors["pellet"], center, max(2, tile // 9))
                if cell in self.freeze_pellets:
                    draw_freeze_power(surface, center, tile)
                if cell in self.speed_pellets:
                    draw_speed_power(surface, center, tile)
        if self.map.door is not None:
            door_rect = pygame.Rect(origin_x + self.map.door[0] * tile + tile // 5, origin_y + self.map.door[1] * tile + tile // 2 - 2, tile - (tile // 5) * 2, 4)
            pygame.draw.rect(surface, pygame.Color("#F9A826"), door_rect, border_radius=4)

    def draw_wall(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        corner = max(4, rect.width // 5)
        pygame.draw.rect(surface, pygame.Color("#071038"), rect, border_radius=corner)
        pygame.draw.rect(surface, self.app.colors["wall"], rect.inflate(-2, -2), width=max(2, rect.width // 8), border_radius=corner)

    def draw_entities(self, surface: pygame.Surface, tile: int, origin_x: int, origin_y: int) -> None:
        draw_pacman_shape(surface, (origin_x + int(self.player_position.x * tile), origin_y + int(self.player_position.y * tile)), max(8, int(tile * 0.46)), self.app.colors["pacman"], facing=self.player_facing)
        for ghost in self.ghosts:
            draw_ghost_shape(surface, (origin_x + int(ghost.position.x * tile), origin_y + int(ghost.position.y * tile)), max(14, int(tile * 0.80)), self.app.colors["ghosts"][ghost.color_key])

    def draw_overlay(self, surface: pygame.Surface) -> None:
        if not self.banner_text:
            return
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 110), overlay.get_rect())
        surface.blit(overlay, (0, 0))
        panel = pygame.Rect(120, surface.get_height() // 2 - 60, surface.get_width() - 240, 120)
        pygame.draw.rect(surface, pygame.Color("#090915"), panel, border_radius=18)
        pygame.draw.rect(surface, self.app.colors["wall"], panel, width=2, border_radius=18)
        font = fit_text_font(self.banner_text, panel.width - 40, 44, candidates=["Segoe UI", "Arial", "Verdana", "Tahoma"])
        surface.blit(font.render(self.banner_text, True, self.app.colors["text"]), font.render(self.banner_text, True, self.app.colors["text"]).get_rect(center=panel.center))
