import threading

from shiny_hunter.config import Config, Pixel, Step
from shiny_hunter.hunt import Hunter


class RecordingKeys:
  def __init__(self) -> None:
    self.pressed: list[str] = []

  def press(self, combo: str, hold: float) -> None:
    self.pressed.append(combo)


class ScriptedScreen:
  def __init__(self, frames: list[str], ready: list[Pixel]) -> None:
    self._frames = frames
    self._index = 0
    self._ready = ready

  def grab(self) -> str:
    frame = self._frames[min(self._index, len(self._frames) - 1)]
    self._index += 1
    return frame

  def color_at(self, shot: str, pixel: Pixel) -> tuple[int, int, int]:
    if shot == "not_ready":
      return (0, 0, 0)
    if shot == "shiny" and pixel not in self._ready:
      return (255, 0, 0)
    return pixel.color


def _hunt(frames: list[str], **overrides: object) -> tuple[Hunter, RecordingKeys, list[int]]:
  ready = Pixel(0, 0, (1, 1, 1))
  shiny = Pixel(1, 1, (10, 10, 10))
  cfg = Config(
    shiny_pixels=[shiny],
    ready_pixels=[ready],
    tolerance=0,
    sequence=[Step("z", wait=0)],
    key_hold=0,
    ready_timeout=0,
    poll_interval=0,
    settle_time=0,
    confirm_captures=1,
    confirm_interval=0,
  )
  if overrides:
    cfg = Config(**{**cfg.__dict__, **overrides})
  keys = RecordingKeys()
  alerts: list[int] = []
  hunter = Hunter(
    cfg,
    keys,
    ScriptedScreen(frames, [ready]),
    threading.Event(),
    lambda: alerts.append(1),
  )
  return hunter, keys, alerts


def test_normal_vuelve_a_mandar_la_secuencia() -> None:
  hunter, keys, alerts = _hunt(["normal"])

  assert hunter.run(max_attempts=2) is False
  assert keys.pressed == ["z", "z"]
  assert alerts == []


def test_timeout_de_ready_no_es_shiny() -> None:
  hunter, keys, alerts = _hunt(["not_ready"])

  assert hunter.run(max_attempts=2) is False
  assert keys.pressed == ["z", "z"]
  assert alerts == []


def test_shiny_que_vuelve_a_normal_no_alerta() -> None:
  hunter, keys, alerts = _hunt(["shiny", "shiny", "normal"])

  assert hunter.run(max_attempts=1) is False
  assert keys.pressed == ["z"]
  assert alerts == []


def test_shiny_confirmado_alerta_y_no_sigue() -> None:
  hunter, keys, alerts = _hunt(["shiny"], confirm_captures=2)

  assert hunter.run(max_attempts=5) is True
  assert keys.pressed == ["z"]
  assert alerts == [1]
