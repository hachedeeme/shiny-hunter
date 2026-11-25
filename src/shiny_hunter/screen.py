from __future__ import annotations

from typing import Any

import mss

from shiny_hunter.config import RGB, Pixel


class Screen:

  def __init__(self, points: list[Pixel]) -> None:
    self._sct = mss.MSS()
    self.left = min(point.x for point in points)
    self.top = min(point.y for point in points)
    self.width = max(point.x for point in points) - self.left + 1
    self.height = max(point.y for point in points) - self.top + 1

  def grab(self) -> Any:
    return self._sct.grab(
      {"left": self.left, "top": self.top, "width": self.width, "height": self.height}
    )

  def color_at(self, shot: Any, pixel: Pixel) -> RGB:
    red, green, blue = shot.pixel(pixel.x - self.left, pixel.y - self.top)
    return (red, green, blue)

  def close(self) -> None:
    self._sct.close()
