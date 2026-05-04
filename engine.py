import time
from parser import MapConfig
from typing import List

from errors import FlyInError
from models import Drone
from traffic import ReservationTable
from visualizer import Visualizer


class SimulationEngine:
    def __init__(self, config: MapConfig, table: ReservationTable) -> None:
        self.config = config
        self.table = table
        self.current_turn = 0
        self.drones: List[Drone] = []

    def run(self, visualizer: Visualizer) -> None:
        if not self.drones:
            raise FlyInError("Simulation engine received 0 drones. Aborting.")
        visualizer.draw_map()
        time.sleep(1.5)

        while not self._all_drones_delivered() and visualizer.running:
            self.current_turn += 1
            turn_movements = self._execute_turn()

            if turn_movements:
                self._display_output(turn_movements)
                visualizer.render_turn(turn_movements)
            else:
                visualizer.root.update()

            time.sleep(0.1)

    def _execute_turn(self) -> List[str]:
        movements: List[str] = []

        for drone in self.drones:

            log = drone.get_log(self.current_turn)
            if log:
                movements.append(log)

        return movements

    def _all_drones_delivered(self) -> bool:
        return (all(drone.is_delivered(self.current_turn)
                for drone in self.drones))

    def _display_output(self, movements: List[str]) -> None:
        print(" ".join(movements))
