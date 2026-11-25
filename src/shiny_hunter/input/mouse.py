from __future__ import annotations

from pynput.mouse import Controller


class Mouse:
  def __init__(self) -> None:
    self._pointer = Controller()

  def position(self) -> tuple[int, int]:
    x, y = self._pointer.position
    return int(x), int(y)
