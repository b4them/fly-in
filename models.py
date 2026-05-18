from typing import Optional, Union

from errors import InvalidCapacityError


class Zone:
    """
    Args:
        name (str): The unique identifier for the zone.
        x (int): The X coordinate on the grid.
        y (int): The Y coordinate on the grid.
        zone_type (str, optional): The classification of the zone
          (normal, restricted, etc.). Defaults to "normal".
        color (Optional[str], optional): The visual
          representation color. Defaults to None.
        max_drones (int, optional): Maximum capacity
          of the zone. Defaults to 1.

    Raises:
        InvalidCapacityError: If max_drones is less than 1.

    """

    def __init__(self, name: str, x: int, y: int, zone_type: str = "normal",
                 color: Optional[str] = None, max_drones: int = 1) -> None:

        if max_drones < 1:
            raise InvalidCapacityError(
                f"Zone '{name}' must have a positive capacity.")
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zone_type: str = zone_type
        self.color: Optional[str] = color
        self.max_drones: int = max_drones


class Connection:
    """
  Represents a bidirectional traversable path between two zones.

  Args:
        zone_a (Zone): The first connecting zone.
        zone_b (Zone): The second connecting zone.
        max (int, optional): The maximum number of drones
          that can travel this connection simultaneously. Defaults to 1.
    """

    def __init__(self, zone_a: Zone, zone_b: Zone, max: int = 1) -> None:
        self.zone_a: Zone = zone_a
        self.zone_b: Zone = zone_b
        self.max: int = max


class Path:
    """
  Tracks the space-time sequence of movements for a specific drone.

  Args:
        drone_name (str): The identifier of the drone owning this path.
        end_name (str): The destination zone name for the drone.
    """

    def __init__(self, drone_name: str, end_name: str) -> None:
        self.drone_name: str = drone_name
        self.end_name: str = end_name
        self._schedule: dict[int, str] = {}
        self.total_turns: int = 0

    def add_movement(self, turn: int, target: Union[Zone, Connection]) -> None:
        """
      Records a movement or wait action in the drone's schedule.

      Args:
            turn (int): The simulation turn the movement concludes.
            target (Union[Zone, Connection]): The zone arriving at,
              or the connection being traversed.
        """
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
    """
  Represents an autonomous vehicle navigating the network.

  Args:
        drone_id (int): The numerical identifier for the drone.
    """

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
