import heapq
import math
from parser import MapConfig
from typing import Any, List, Set, Tuple

from errors import FlyInError, NoPathFoundError
from models import Drone, Path, Zone
from traffic import ReservationTable


class SpaceTime:
    def __init__(self, config: MapConfig, table: ReservationTable) -> None:
        self.config = config
        self.table = table
        self._count = 0

    def heuristic(self, zone: Zone, goal: Zone) -> float:
        return float(math.sqrt(
            math.pow(goal.x - zone.x, 2) +
            math.pow(goal.y - zone.y, 2)
        ))

    def solve(self, drones: List[Drone]) -> None:

        if self.config.start_hub is None or self.config.end_hub is None:
            raise FlyInError("Simulation requires both a start and end hub.")
        for drone in drones:
            path_obj = self._find_path(
                drone.name, self.config.start_hub, self.config.end_hub)

            drone.set_path(path_obj)

    def _find_path(self, drone_name: str, start: Zone, end: Zone) -> Path:
        self._count += 1
        start_h = self.heuristic(start, end)
        pq: List[Tuple[float, int, int, str, List[Any]]] = [
            (start_h, self._count, 0, start.name, [])]
        visited: Set[Tuple[str, int]] = set()

        while pq:
            _, count, turn, curr_name, history = heapq.heappop(pq)

            if curr_name == end.name:
                return self._build_path_object(drone_name, end.name, history)

            if (curr_name, turn) in visited:
                continue
            visited.add((curr_name, turn))

            curr_zone = self.config.zones[curr_name]

            wait_turn = turn + 1
            if self.table.is_zone_available(curr_zone, wait_turn):
                new_g = wait_turn
                new_f = new_g + self.heuristic(curr_zone, end)

                new_history_wait = history + [(wait_turn, "wait", curr_zone)]
                self._count += 1
                heapq.heappush(
                    pq, (new_f, self._count,
                         wait_turn, curr_name, new_history_wait))

            for connection in self.config.graph[curr_name]:
                neighbor = (connection.zone_b if connection.zone_a.name ==
                            curr_name else connection.zone_a)

                step_cost = 2 if neighbor.zone_type == "restricted" else 1
                arrival_turn = turn + step_cost

                if (self.table.is_connection_available(connection, turn + 1)
                        and
                        self.table.is_zone_available(neighbor, arrival_turn)):

                    vip_dis = 0.5 if neighbor.zone_type == "priority" else 0.0
                    new_f = arrival_turn + \
                        self.heuristic(neighbor, end) - vip_dis

                    if step_cost == 2:
                        new_move = (history +
                                    [(arrival_turn, "move_restricted",
                                      (neighbor, connection))])
                    else:
                        new_move = (history +
                                    [(arrival_turn,
                                      "move_zone", (neighbor, connection))])

                    heapq.heappush(
                        pq, (new_f, self._count,
                             arrival_turn, neighbor.name, new_move))

        raise NoPathFoundError(
            f"No valid Space-Time path found for drone {drone_name}.")

    def _build_path_object(self, drone_name: str,
                           end: str,
                           history: List[Tuple[int, str, Any]]) -> Path:
        path_obj = Path(drone_name, end)

        for turn, action, data in history:
            if action == "wait":
                zone = data
                self.table.reserve_zone(zone.name, turn)

            elif action == "move_zone":
                zone, conn = data
                self.table.reserve_connection(
                    conn.zone_a.name, conn.zone_b.name, turn)
                self.table.reserve_zone(zone.name, turn)
                path_obj.add_movement(turn, zone)

            elif action == "move_restricted":
                zone, conn = data
                connection_turn = turn - 1

                self.table.reserve_connection(
                    conn.zone_a.name, conn.zone_b.name, connection_turn)
                path_obj.add_movement(connection_turn, conn)

                self.table.reserve_zone(zone.name, turn)
                path_obj.add_movement(turn, zone)

        return path_obj
