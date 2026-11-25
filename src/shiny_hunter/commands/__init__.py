"""Registro de subcomandos. Cada comando agrega su register a REGISTRARS."""

from __future__ import annotations

from argparse import _SubParsersAction

from shiny_hunter.commands.calibrate import register as register_calibrate

REGISTRARS = [register_calibrate]


def register_all(subparsers: _SubParsersAction) -> None:
  for register in REGISTRARS:
    register(subparsers)
