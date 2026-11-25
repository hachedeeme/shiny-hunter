"""Aviso sonoro al confirmar un shiny."""

from __future__ import annotations

import sys
import time


def alert(times: int = 6) -> None:
  for _ in range(times):
    if sys.platform == "win32":
      import winsound

      winsound.Beep(1200, 300)
      time.sleep(0.1)
    else:
      sys.stdout.write("\a")
      sys.stdout.flush()
      time.sleep(0.4)
