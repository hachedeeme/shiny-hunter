from shiny_hunter._platform import ensure_dpi_aware

ensure_dpi_aware()


def main() -> int:
  from shiny_hunter.cli import main as cli_main

  return cli_main()
