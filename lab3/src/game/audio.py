"""Audio service."""

from __future__ import annotations

import pygame

from .core import ROOT_DIR


class AudioManager:
    def __init__(self, settings: dict):
        self.enabled = False
        self.music_settings = settings.get("music", {})
        self.sfx_settings = settings.get("sfx", {})
        self.music_volume = float(self.music_settings.get("volume", 0.4))
        self.sfx_volume = float(settings.get("sfx_volume", 0.6))
        self.current_music: str | None = None
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        try:
            pygame.mixer.init()
        except pygame.error:
            return
        self.enabled = True

    def play_music(self, key: str) -> None:
        if not self.enabled:
            return
        path = self.music_settings.get(key)
        if not path or path == self.current_music:
            return
        full_path = ROOT_DIR / path
        if not full_path.exists():
            return
        try:
            pygame.mixer.music.load(full_path.as_posix())
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1)
            self.current_music = path
        except pygame.error:
            self.current_music = None

    def play_sfx(self, key: str) -> None:
        if not self.enabled:
            return
        path = self.sfx_settings.get(key)
        if not path:
            return
        if key not in self.sounds:
            full_path = ROOT_DIR / path
            if not full_path.exists():
                return
            try:
                sound = pygame.mixer.Sound(full_path.as_posix())
            except pygame.error:
                return
            sound.set_volume(self.sfx_volume)
            self.sounds[key] = sound
        self.sounds[key].play()
