from __future__ import annotations

import sys

_dpi_configured = False


def ensure_dpi_aware() -> None:
  """
  Declara el proceso como "DPI aware" en Windows. Es idempotente.
  Con escalado de pantalla (125%, 150%...) Windows virtualiza las coordenadas
  y las de ``pynput`` (mouse) y ``mss`` (captura) dejan de coincidir. Declarar
  el proceso como DPI aware hace que ambas trabajen en pixeles físicos.

  IMPORTANTE: debe llamarse ANTES de importar ``pynput`` y ``mss``. Por eso se
  invoca desde ``shiny_hunter/__init__.py``, que Python ejecuta antes que
  cualquier submódulo del paquete.

  En otros sistemas operativos no hace nada.
  """
  global _dpi_configured
  if _dpi_configured:
    return
  _dpi_configured = True

  if sys.platform != "win32":
    return

  try:
    import ctypes

    ctypes.windll.shcore.SetProcessDpiAwareness(2)
  except Exception:  # noqa: BLE001 - ya configurado o no disponible
    pass
