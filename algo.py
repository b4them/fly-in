import heapq
from typing import List, Tuple, Set
from parser import MapConfig
from traffic import ReservationTable
from models import Zone, Path, Drone, Connection


class SpaceTime:
    def __init__(self, config: MapConfig, table: ReservationTable) -> None:
        self.config = config
        self.table = table
        self.turns = 0

    def heuristic(self, zone: Zone, goal: Zone) -> float:
        return ((goal.x - zone.x) ** 2 + (goal.y - zone.y) ** 2)**0.5

    def solve(self, drones: List[Drone]) -> None:
        for drone in drones:
            path_obj = self.distance(
                drone.name, self.config.start_hub, self.config.end_hub)

            drone.set_path(path_obj)

    def distance(self, drone_name: str, start: Zone, end: Zone) -> Path:
        start_h = self.heuristic(start, end)
        pq = [(start_h, 0, start.name, [])]
        visited: Set[Tuple[str, int]] = set()

        while pq:
            f, turn, curr_name, history = heapq.heappop(pq)

            if curr_name == end.name:
                return self._build_path_object(drone_name, end.name, history)

            if (curr)
