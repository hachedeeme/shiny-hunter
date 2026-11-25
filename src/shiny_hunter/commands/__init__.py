"""Registro de subcomandos. Cada comando agrega su register a REGISTRARS."""

from __future__ import annotations

from argparse import _SubParsersAction

from shiny_hunter.commands.calibrate import register as register_calibrate
from shiny_hunter.commands.check import register as register_check
from shiny_hunter.commands.hunt import register as register_hunt

REGISTRARS = [register_calibrate, register_check, register_hunt]


def register_all(subparsers: _SubParsersAction) -> None:
  for register in REGISTRARS:
    register(subparsers)
