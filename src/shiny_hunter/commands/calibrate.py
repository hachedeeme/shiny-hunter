from __future__ import annotations

import argparse
import sys
import threading

import mss

from shiny_hunter.input.keyboard import Keyboard
from shiny_hunter.input.mouse import Mouse


def register(subparsers: argparse._SubParsersAction) -> None:
  cmd = subparsers.add_parser(
    "calibrate",
    help="Muestra posición y color del pixel bajo el mouse.",
  )
  cmd.add_argument("--mark-key", default="f9", help="Tecla para anotar el pixel (default: f9).")
  cmd.add_argument("--stop-key", default="f12", help="Tecla para salir (default: f12).")
  cmd.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
  pointer, keys = Mouse(), Keyboard()
  stop, mark = threading.Event(), threading.Event()
  listener = keys.listen(
    [(keys.parse_key(args.stop_key), stop.set), (keys.parse_key(args.mark_key), mark.set)]
  )
  print(
    f"Mové el mouse sobre el pixel que querés medir.\n"
    f"  [{args.mark_key.upper()}] anota el pixel actual  |  "
    f"[{args.stop_key.upper()}] o Ctrl+C para salir\n"
  )
  try:
    with mss.MSS() as sct:
      while not stop.is_set():
        x, y = pointer.position()
        try:
          r, g, b = sct.grab({"left": x, "top": y, "width": 1, "height": 1}).pixel(0, 0)
        except Exception as exc:  # noqa: BLE001
          sys.stdout.write(f"\rError de captura: {exc}".ljust(70))
          sys.stdout.flush()
          stop.wait(0.3)
          continue
        line = f"x={x} y={y} color=({r}, {g}, {b})"
        if mark.is_set():
          mark.clear()
          sys.stdout.write("\r" + " " * 70 + "\r")
          print(f'ANOTADO -> {{"x": {x}, "y": {y}, "color": [{r}, {g}, {b}]}}')
        else:
          sys.stdout.write("\r" + line.ljust(70))
          sys.stdout.flush()
        stop.wait(0.1)
  except KeyboardInterrupt:
    pass
  finally:
    listener.stop()
    print()
  return 0
