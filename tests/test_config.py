import json

import pytest

from shiny_hunter.config import Config, ConfigError, Pixel, Step, evaluate, load_config


def test_pixel_matches_dentro_de_la_tolerancia() -> None:
  pixel = Pixel(1, 2, (10, 20, 30))

  assert pixel.matches((12, 20, 30), tolerance=5)
  assert not pixel.matches((20, 20, 30), tolerance=5)


def test_evaluate_shiny_cuando_esta_listo_y_todos_difieren() -> None:
  ready = Pixel(0, 0, (1, 1, 1))
  shiny = Pixel(1, 1, (10, 10, 10))
  cfg = Config(shiny_pixels=[shiny], ready_pixels=[ready], tolerance=0)

  assert evaluate(cfg, [(1, 1, 1)], [(0, 0, 0)]) == "shiny"


def test_evaluate_normal_si_un_shiny_sigue_igual() -> None:
  shiny = Pixel(1, 1, (10, 10, 10))
  cfg = Config(shiny_pixels=[shiny], tolerance=0)

  assert evaluate(cfg, [], [(10, 10, 10)]) == "normal"


def test_evaluate_no_es_shiny_si_ready_no_coincide() -> None:
  ready = Pixel(0, 0, (1, 1, 1))
  shiny = Pixel(1, 1, (10, 10, 10))
  cfg = Config(shiny_pixels=[shiny], ready_pixels=[ready], tolerance=0)

  assert evaluate(cfg, [(9, 9, 9)], [(0, 0, 0)]) == "not_ready"


def test_load_config_con_solo_shiny_pixels(tmp_path) -> None:
  path = tmp_path / "config.json"
  path.write_text(
    json.dumps(
      {
        "sequence": [{"keys": "x", "wait": 1}],
        "shiny_pixels": [{"x": 1, "y": 2, "color": [3, 4, 5]}],
      }
    ),
    encoding="utf-8",
  )

  cfg = load_config(str(path))

  assert cfg.shiny_pixels == [Pixel(1, 2, (3, 4, 5))]
  assert cfg.ready_pixels == []
  assert cfg.tolerance == 12
  assert cfg.stop_key == "f12"
  assert cfg.sequence == [Step("x", wait=1.0)]
  assert cfg.key_hold == 0.05


def test_load_config_sin_shiny_pixels_falla(tmp_path) -> None:
  path = tmp_path / "config.json"
  path.write_text("{}", encoding="utf-8")

  with pytest.raises(ConfigError, match="shiny_pixels"):
    load_config(str(path))
