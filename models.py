from typing import Optional, Union


class Zone:
    def __init__(self, name: str, x: int, y: int, zone_type: str = "normal",
                 color: Optional[str] = None, max_drones: int = 1) -> None:
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zone_type: str = zone_type
        self.color: Optional[str] = color
        self.max_drones: int = max_drones


class Connection:
    def __init__(self, zone_a: Zone, zone_b: Zone, max: int = 1) -> None:
        self.zone_a: Zone = zone_a
        self.zone_b: Zone = zone_b
        self.max: int = max


class Path:
    def __init__(self, drone_name: str, end_name: str) -> None:
        self.drone_name: str = drone_name
        self.end_name: str = end_name
        self._schedule: dict[int, str] = {}
        self.total_turns: int = 0

    def add_movement(self, turn: int, target: Union[Zone, Connection]) -> None:
        if isinstance(target, Zone):
            name = target.name
        else:
            name = f"{target.zone_a.name}-{target.zone_b.name}"

        self._schedule[turn] = f"{self.drone_name}-{name}"
        self.total_turns = max(self.total_turns, turn)

    def get_output(self, turn: int) -> Optional[str]:
        return self._schedule.get(turn)

    def is_finished(self, turn: int) -> bool:
        for t, move_str in self._schedule.items():
            if t < turn and move_str.endswith(f"-{self.end_name}"):
                return True
        return False


class Drone:
    def __init__(self, drone_id: int) -> None:
        self.id: int = drone_id
        self.name: str = f"D{drone_id}"
        self.path: Optional[Path] = None

    def set_path(self, path: Path) -> None:
        self.path = path

    def is_delivered(self, turn: int) -> bool:
        if not self.path:
            return False

        return self.path.is_finished(turn + 1)

    def get_log(self, turn: int) -> Optional[str]:
        if not self.path or self.path.is_finished(turn):
            return None

        return self.path.get_output(turn)
