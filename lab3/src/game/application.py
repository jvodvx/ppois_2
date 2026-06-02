"""Application bootstrap and scene coordination."""

from __future__ import annotations

import json

import pygame

from .audio import AudioManager
from .core import CONFIG_DIR, DATA_DIR, hex_color, load_json, save_json
from .gameplay import GameScene
from .levels import GameMap, load_map
from .scenes.base import Scene
from .scenes.menus import HelpScene, MapSelectScene, MenuScene, RecordsScene


class PacmanApp:
    def __init__(self):
        pygame.init()
        self.config = load_json(CONFIG_DIR / "app.json")
        color_config = load_json(CONFIG_DIR / "colors.json")
        self.colors = {
            "background": hex_color("#000000"),
            "wall": hex_color("#2121FF"),
            "floor": hex_color("#050505"),
            "pellet": hex_color("#F5F5F5"),
            "power_pellet": hex_color("#FFD1DC"),
            "pacman": hex_color("#FFD200"),
            "text": hex_color("#F4F1DE"),
            "accent": hex_color("#E07A5F"),
            "ghosts": {
                "chaser": hex_color("#FF3030"),
                "patrol": hex_color("#00FFFF"),
            },
        }
        self.colors.update({key: hex_color(value) for key, value in color_config.items() if isinstance(value, str)})
        ghost_colors = {key: hex_color(value) for key, value in color_config.get("ghosts", {}).items()}
        if ghost_colors:
            self.colors["ghosts"] = ghost_colors

        window = self.config["window"]
        self.windowed_size = (int(window["width"]), int(window["height"]))
        desktop_sizes = pygame.display.get_desktop_sizes()
        self.display_size = desktop_sizes[0] if desktop_sizes else self.windowed_size
        self.fullscreen = bool(window.get("fullscreen", False))
        self.screen = self.create_display()
        pygame.display.set_caption(window["title"])

        self.clock = pygame.time.Clock()
        self.running = True
        self.audio = AudioManager(load_json(CONFIG_DIR / "audio.json"))
        self.map_cache: dict[str, GameMap] = {}
        self.records_path = DATA_DIR / "records.json"

        self.game_scene = GameScene(self)
        self.scenes: dict[str, Scene] = {
            "menu": MenuScene(self),
            "map_select": MapSelectScene(self),
            "help": HelpScene(self),
            "records": RecordsScene(self),
            "game": self.game_scene,
        }
        self.current_scene = self.scenes["menu"]
        self.current_scene.on_enter()

    def create_display(self) -> pygame.Surface:
        flags = pygame.FULLSCREEN if self.fullscreen else pygame.RESIZABLE
        size = self.display_size if self.fullscreen else self.windowed_size
        return pygame.display.set_mode(size, flags)

    def get_map(self, name: str) -> GameMap:
        if name not in self.map_cache:
            self.map_cache[name] = load_map(name)
        return self.map_cache[name]

    def start_new_game(self, campaign_key: str = "classic") -> None:
        self.game_scene.start_new_game(campaign_key)
        self.change_scene("game")

    def load_records(self) -> list[dict]:
        if not self.records_path.exists():
            return []
        try:
            data = load_json(self.records_path)
        except (OSError, json.JSONDecodeError):
            return []
        return data if isinstance(data, list) else []

    def save_record(self, record: dict) -> None:
        records = self.load_records()
        records.append({"name": record.get("name", "PLAYER"), "score": int(record.get("score", 0))})
        records.sort(key=lambda item: item.get("score", 0), reverse=True)
        save_json(self.records_path, records[:3])

    def toggle_fullscreen(self) -> None:
        self.fullscreen = not self.fullscreen
        self.screen = self.create_display()

    def change_scene(self, scene_name: str) -> None:
        self.current_scene = self.scenes[scene_name]
        self.current_scene.on_enter()

    def quit(self) -> None:
        self.running = False

    def run(self, max_frames: int | None = None) -> None:
        frames = 0
        while self.running:
            dt = self.clock.tick(int(self.config["window"]["fps"])) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and event.mod & pygame.KMOD_ALT:
                    self.toggle_fullscreen()
                elif event.type == pygame.VIDEORESIZE and not self.fullscreen:
                    self.windowed_size = (max(800, event.w), max(680, event.h))
                    self.screen = self.create_display()
                else:
                    self.current_scene.handle_event(event)
            self.current_scene.update(dt)
            self.current_scene.draw(self.screen)
            pygame.display.flip()
            frames += 1
            if max_frames is not None and frames >= max_frames:
                break
        pygame.quit()


def main() -> None:
    app = PacmanApp()
    app.run()
