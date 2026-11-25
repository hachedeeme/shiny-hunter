from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from shiny_hunter.input.keyboard import Keyboard

RGB = tuple[int, int, int]
Verdict = Literal["not_ready", "normal", "shiny"]


class ConfigError(Exception):
  """Error de configuración legible para el usuario."""


@dataclass(frozen=True)
class Pixel:
  x: int
  y: int
  color: RGB

  def matches(self, current: RGB, tolerance: int) -> bool:
    return all(abs(a - b) <= tolerance for a, b in zip(self.color, current, strict=True))


@dataclass(frozen=True)
class Config:
  shiny_pixels: list[Pixel]
  ready_pixels: list[Pixel] = field(default_factory=list)
  tolerance: int = 12
  stop_key: str = "f12"


def evaluate(cfg: Config, ready_now: list[RGB], shiny_now: list[RGB]) -> Verdict:
  ready_ok = all(
    pixel.matches(current, cfg.tolerance)
    for pixel, current in zip(cfg.ready_pixels, ready_now, strict=True)
  )
  if not ready_ok:
    return "not_ready"
  all_different = all(
    not pixel.matches(current, cfg.tolerance)
    for pixel, current in zip(cfg.shiny_pixels, shiny_now, strict=True)
  )
  return "shiny" if all_different else "normal"


def load_config(path: str) -> Config:
  file = Path(path)
  try:
    raw = json.loads(file.read_text(encoding="utf-8"))
  except FileNotFoundError:
    raise ConfigError(f"No existe el archivo de configuración: {file}") from None
  except json.JSONDecodeError as exc:
    raise ConfigError(f"{file} no es un JSON válido: {exc}") from None
  except OSError as exc:
    raise ConfigError(f"No pude leer {file}: {exc}") from None
  if not isinstance(raw, dict):
    raise ConfigError(f"{file} no es un objeto JSON.")

  shiny = _parse_pixels(raw.get("shiny_pixels", []), "shiny_pixels")
  if not shiny:
    raise ConfigError("Definí al menos un pixel en 'shiny_pixels'.")
  ready = _parse_pixels(raw.get("ready_pixels", []), "ready_pixels")

  try:
    tolerance = int(raw.get("tolerance", 12))
    stop_key = str(raw.get("stop_key", "f12"))
  except (TypeError, ValueError) as exc:
    raise ConfigError(f"Valor numérico inválido en la config: {exc}") from None

  try:
    Keyboard().parse_key(stop_key)
  except ValueError as exc:
    raise ConfigError(str(exc)) from None

  return Config(
    shiny_pixels=shiny,
    ready_pixels=ready,
    tolerance=tolerance,
    stop_key=stop_key,
  )


def _parse_pixels(items: object, name: str) -> list[Pixel]:
  if not isinstance(items, list):
    raise ConfigError(f"'{name}' debe ser una lista.")
  pixels: list[Pixel] = []
  for index, item in enumerate(items, start=1):
    try:
      if not isinstance(item, dict):
        raise TypeError
      color = tuple(int(channel) for channel in item["color"])
      if len(color) != 3:
        raise ValueError
      pixels.append(Pixel(int(item["x"]), int(item["y"]), color))
    except KeyError, TypeError, ValueError:
      raise ConfigError(
        f"'{name}' #{index} inválido: se necesita x, y y color [r, g, b]."
      ) from None
  return pixels
