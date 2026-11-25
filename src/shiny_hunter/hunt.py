from __future__ import annotations

import threading
import time
from collections.abc import Callable
from typing import Any

from shiny_hunter.config import Config, evaluate
from shiny_hunter.input.keyboard import Keyboard
from shiny_hunter.screen import Screen


class Hunter:
  def __init__(
    self,
    cfg: Config,
    keys: Keyboard,
    screen: Screen,
    stop: threading.Event,
    alert: Callable[[], None],
  ) -> None:
    self.cfg = cfg
    self.keys = keys
    self.screen = screen
    self.stop = stop
    self._alert = alert

  def run(self, max_attempts: int = 0) -> bool:
    attempt = 0
    while not self.stop.is_set():
      if max_attempts and attempt >= max_attempts:
        print(f"Se alcanzó el máximo de {max_attempts} intentos.")
        break
      attempt += 1
      if not self._run_sequence():
        break
      shot = self._wait_ready()
      if self.stop.is_set():
        break
      if shot is None:
        print(
          f"Intento {attempt}: la pantalla esperada no apareció en "
          f"{self.cfg.ready_timeout:.0f}s (desincronizado). Reinicio."
        )
        continue
      if self.stop.wait(self.cfg.settle_time):
        break
      if self._verdict(self.screen.grab()) == "shiny" and self._confirm():
        print(
          f"SHINY ENCONTRADO en el intento {attempt}. "
          "El script NO manda más teclas: no toques nada y guardá la partida."
        )
        self._alert()
        return True
      print(f"Intento {attempt}: normal")
    print(f"Detenido. Intentos: {attempt}.")
    return False

  def _run_sequence(self) -> bool:
    for step in self.cfg.sequence:
      if self.stop.is_set():
        return False
      hold = self.cfg.key_hold if step.hold is None else step.hold
      self.keys.press(step.keys, hold)
      if self.stop.wait(step.wait):
        return False
    return True

  def _wait_ready(self) -> Any:
    deadline = time.monotonic() + self.cfg.ready_timeout
    while not self.stop.is_set():
      shot = self.screen.grab()
      if self._verdict(shot) != "not_ready":
        return shot
      if time.monotonic() >= deadline or self.stop.wait(self.cfg.poll_interval):
        return None
    return None

  def _confirm(self) -> bool:
    for _ in range(self.cfg.confirm_captures):
      if self.stop.wait(self.cfg.confirm_interval):
        return False
      if self._verdict(self.screen.grab()) != "shiny":
        return False
    return True

  def _verdict(self, shot: Any) -> str:
    ready_now = [self.screen.color_at(shot, pixel) for pixel in self.cfg.ready_pixels]
    shiny_now = [self.screen.color_at(shot, pixel) for pixel in self.cfg.shiny_pixels]
    return evaluate(self.cfg, ready_now, shiny_now)
