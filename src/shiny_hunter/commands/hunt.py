from __future__ import annotations

import argparse
import sys
import threading

from shiny_hunter.alerts import alert
from shiny_hunter.config import ConfigError, load_config
from shiny_hunter.hunt import Hunter
from shiny_hunter.input.keyboard import Keyboard
from shiny_hunter.screen import Screen


def register(subparsers: argparse._SubParsersAction) -> None:
  cmd = subparsers.add_parser("hunt", help="Repite el soft reset hasta confirmar un shiny.")
  cmd.add_argument("-c", "--config", default="config.json")
  cmd.add_argument("--countdown", type=int, default=5)
  cmd.add_argument("--max-attempts", type=int, default=0, help="0 = sin límite.")
  cmd.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
  try:
    cfg = load_config(args.config)
  except ConfigError as exc:
    print(f"Error de configuración: {exc}", file=sys.stderr)
    return 2
  if not cfg.sequence:
    print("Error de configuración: 'sequence' no puede estar vacía.", file=sys.stderr)
    return 2

  keys = Keyboard()
  stop = threading.Event()
  listener = keys.listen([(keys.parse_key(cfg.stop_key), stop.set)])
  screen = Screen(cfg.ready_pixels + cfg.shiny_pixels)
  try:
    if not _countdown(args.countdown, stop):
      return 1
    Hunter(cfg, keys, screen, stop, alert).run(args.max_attempts)
  except KeyboardInterrupt:
    return 1
  finally:
    screen.close()
    listener.stop()
  return 0


def _countdown(seconds: int, stop: threading.Event) -> bool:
  for remaining in range(seconds, 0, -1):
    print(f"Empezando en {remaining}... (dejá Playback visible y en primer plano)")
    if stop.wait(1):
      return False
  return True
