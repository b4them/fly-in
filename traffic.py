from typing import Dict, Tuple

from errors import FlyInError
from models import Connection, Zone


class ReservationTable:
    """
  A 3D space-time grid (X, Y, Time) to prevent drone collisions.

  Tracks the exact occupancy of every zone and connection at any given
    simulation turn to guarantee paths do not violate capacity limits.

  Args:
        start_node (str): The name of the map's starting hub.
        end_node (str): The name of the map's ending hub.
    """

    def __init__(self, start_node: str, end_node: str) -> None:
        self.start_name: str = start_node
        self.end_name: str = end_node

        self.zone_occupancy: Dict[Tuple[str, int], int] = {}
        self.connection_occupancy: Dict[Tuple[str, str, int], int] = {}

    def is_zone_available(self, zone: Zone, turn: int) -> bool:
        """
      Checks if a zone has available capacity during a specific turn.

      Args:
            zone (Zone): The zone to check.
            turn (int): The specific simulation turn.

      Returns:
            bool: True if the zone can accommodate another
              drone, False otherwise.
        """
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
        """
      Claims one capacity slot in a zone for a specific turn.

      Args:
            zone_name (str): The name of the zone to reserve.
            turn (int): The specific simulation turn.

      Raises:
            FlyInError: If the provided turn is a negative integer.
        """
        if turn < 0:
            raise FlyInError(
                f"Cannot reserve zone '{zone_name}' for negative turn {turn}")
        key = (zone_name, turn)
        self.zone_occupancy[key] = self.zone_occupancy.get(key, 0) + 1

    def reserve_connection(self, zone_a: str, zone_b: str, turn: int) -> None:
        pair = tuple(sorted((zone_a, zone_b)))
        key = (pair[0], pair[1], turn)
        self.connection_occupancy[key] = self.connection_occupancy.get(
            key, 0) + 1
