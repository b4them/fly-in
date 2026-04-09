from typing import Optional


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
