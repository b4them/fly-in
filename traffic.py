from typing import Dict, Tuple

from .types import Connection, Zone


class ReservationTable:
    def __init__(self, start_node: str, end_node: str) -> None:
        self.start_name: str = start_node
        self.end_name: str = end_node

        self.zone_occupancy: Dict[Tuple[str, int], int] = {}
        self.connection_occupancy: Dict[Tuple[str, str, int], int] = {}

    def is_zone_available(self, zone: Zone, turn: int) -> bool:
        if zone.zone_type == "blocked":
            return False

        if zone.name == self.start_name or zone.name == self.end_name:
            return True

        count = self.zone_occupancy.get((zone.name, turn), 0)
        return count < zone.max_drones

    def is_connection_available(self, conn: Connection, turn: int) -> bool:
        pair = tuple(sorted((conn.zone_a.name, conn.zone_b.name)))
        current_count = self.connection_occupancy.get(
            (pair[0], pair[1], turn), 0)

        return current_count < conn.max

    def reserve_zone(self, zone_name: str, turn: int) -> None:
        key = (zone_name, turn)
        self.zone_occupancy[key] = self.zone_occupancy.get(key, 0) + 1

    def reserve_connection(self, zone_a: str, zone_b: str, turn: int) -> None:
        pair = tuple(sorted((zone_a, zone_b)))
        key = (pair[0], pair[1], turn)
        self.connection_occupancy[key] = self.connection_occupancy.get(
            key, 0) + 1
