from __future__ import annotations

import argparse

from shiny_hunter.commands import register_all


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(description="Shiny hunter por soft reset (Epilogue Playback).")
  sub = parser.add_subparsers(dest="command", required=True)
  register_all(sub)
  return parser


def main() -> int:
  args = build_parser().parse_args()
  return args.func(args)
