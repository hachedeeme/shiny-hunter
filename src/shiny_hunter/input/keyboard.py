"""Teclas globales. Único uso de pynput.keyboard."""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

from pynput import keyboard

_SPECIAL_KEYS = {
  "ctrl": keyboard.Key.ctrl,
  "shift": keyboard.Key.shift,
  "alt": keyboard.Key.alt,
  "enter": keyboard.Key.enter,
  "space": keyboard.Key.space,
  "tab": keyboard.Key.tab,
  "esc": keyboard.Key.esc,
  "backspace": keyboard.Key.backspace,
  "up": keyboard.Key.up,
  "down": keyboard.Key.down,
  "left": keyboard.Key.left,
  "right": keyboard.Key.right,
}


class Keyboard:
  def parse_key(self, name: str) -> Any:
    """Convierte 'ctrl', 'f12', 'z'... en algo que pynput entienda."""
    n = name.strip().lower()
    if n in _SPECIAL_KEYS:
      return _SPECIAL_KEYS[n]
    if re.fullmatch(r"f([1-9]|1[0-9]|20)", n):
      return getattr(keyboard.Key, n)
    if len(n) == 1:
      return n
    raise ValueError(f"Tecla desconocida: {name!r}")

  def _matches(self, pressed: Any, target: Any) -> bool:
    if pressed == target:
      return True
    char = getattr(pressed, "char", None)
    return isinstance(target, str) and char is not None and char.lower() == target

  def listen(self, handlers: list[tuple[Any, Callable[[], None]]]) -> keyboard.Listener:
    """Escucha teclas globales. handlers: lista de (tecla ya parseada, callback)."""

    def on_press(key: Any) -> None:
      for target, callback in handlers:
        if self._matches(key, target):
          callback()

    listener = keyboard.Listener(on_press=on_press)
    listener.daemon = True
    listener.start()
    return listener
