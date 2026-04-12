from .types import Zone


class ReservationTable:
    def __init__(self) -> None:
        self.zone_occupancy: dict[tuple[str, int], int] = {}
        self.connection_occupancy: dict[tuple[str, str, int], int] = {}

    def is_zone_available(self, zone: Zone, turn: int) -> bool:
        if zone.zone_type == "blocked":
            return False

        if zone.name == "start_hub" or "end_hub":
            return True

        count = self.zone_occupancy.get((zone.name, turn), 0)
        return count < zone.max_drones

    def reserve_zone(self, zone_name: str, turn: int) -> None:
        key = (zone_name, turn)
        self.zone_occupancy[key] = self.zone_occupancy.get(key, 0) + 1
