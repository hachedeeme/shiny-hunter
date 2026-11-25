from __future__ import annotations

import argparse
import sys
import threading

from shiny_hunter.config import RGB, Config, ConfigError, evaluate, load_config
from shiny_hunter.input.keyboard import Keyboard
from shiny_hunter.screen import Screen


def register(subparsers: argparse._SubParsersAction) -> None:
  cmd = subparsers.add_parser("check", help="Evalúa la pantalla actual una sola vez.")
  cmd.add_argument("-c", "--config", default="config.json")
  cmd.add_argument("--countdown", type=int, default=5)
  cmd.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
  try:
    cfg = load_config(args.config)
  except ConfigError as exc:
    print(f"Error de configuración: {exc}", file=sys.stderr)
    return 2

  keys = Keyboard()
  stop = threading.Event()
  listener = keys.listen([(keys.parse_key(cfg.stop_key), stop.set)])
  try:
    if not _countdown(args.countdown, stop):
      return 1
    screen = Screen(cfg.ready_pixels + cfg.shiny_pixels)
    try:
      shot = screen.grab()
      ready_now = [screen.color_at(shot, pixel) for pixel in cfg.ready_pixels]
      shiny_now = [screen.color_at(shot, pixel) for pixel in cfg.shiny_pixels]
    finally:
      screen.close()
    _report(cfg, ready_now, shiny_now)
  except KeyboardInterrupt:
    return 1
  finally:
    listener.stop()
  return 0


def _countdown(seconds: int, stop: threading.Event) -> bool:
  for remaining in range(seconds, 0, -1):
    print(f"Empezando en {remaining}... (dejá Playback visible y en primer plano)")
    if stop.wait(1):
      return False
  return True


def _report(cfg: Config, ready_now: list[RGB], shiny_now: list[RGB]) -> None:
  print("\nPixeles de 'pantalla lista':")
  if not cfg.ready_pixels:
    print("  (ninguno definido)")
  for pixel, current in zip(cfg.ready_pixels, ready_now, strict=True):
    state = "OK" if pixel.matches(current, cfg.tolerance) else "NO COINCIDE"
    print(f"  ({pixel.x},{pixel.y}) esperado {pixel.color} actual {current} -> {state}")

  print("\nPixeles de 'shiny' (color de un pokemon normal):")
  for pixel, current in zip(cfg.shiny_pixels, shiny_now, strict=True):
    state = "igual al normal" if pixel.matches(current, cfg.tolerance) else "DIFERENTE"
    print(f"  ({pixel.x},{pixel.y}) normal {pixel.color} actual {current} -> {state}")

  print()
  result = evaluate(cfg, ready_now, shiny_now)
  if result == "not_ready":
    print("Resultado: la pantalla NO está en el estado esperado (no se evalúa shiny).")
  elif result == "shiny":
    print("Resultado: SHINY (todos los pixeles difieren del color normal).")
  else:
    print("Resultado: normal.")
