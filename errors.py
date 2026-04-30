import sys


def display_error(message: str) -> None:
    sys.stderr.write(f"[ERROR]: {message}\n")


class MapParsingError(Exception):
    def __init__(self, *args: str) -> None:
        super().__init__(*args)


class InvalidCapacityError(Exception):
    def __init__(self, *args: str) -> None:
        super().__init__(*args)


class NoPathFoundError(Exception):
    def __init__(self, *args: str) -> None:
        super().__init__(*args)
