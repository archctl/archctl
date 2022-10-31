"""Allow archctl to be executable through `python -m archctl`."""
from archctl.cli import main


if __name__ == "__main__":  # pragma: no cover
    main(prog_name="archctl")
