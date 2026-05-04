import sys


def display_error(message: str) -> None:
    """Prints a formatted error message to stderr."""
    sys.stderr.write(f"[ERROR]: {message}\n")


class FlyInError(Exception):
    pass


class MapParsingError(FlyInError):
    def __init__(self, line_nb: int, message: str) -> None:
        self.line_nb = line_nb
        self.message = message
        super().__init__(f"Line {line_nb}: {message}")


class InvalidCapacityError(FlyInError):
    pass


class DuplicateHubError(FlyInError):
    pass


class InvalidZoneTypeError(FlyInError):
    pass


class NoPathFoundError(FlyInError):
    pass
