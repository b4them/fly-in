import time
from parser import MapConfig
from typing import List

from errors import FlyInError
from models import Drone
from traffic import ReservationTable
from visualizer import Visualizer


class SimulationEngine:
    """
  Executes the calculated drone paths turn-by-turn.

  Args:
      config (MapConfig): The parsed configuration of the map.
      table (ReservationTable): The global occupancy tracker.
    """

    def __init__(self, config: MapConfig, table: ReservationTable) -> None:
        self.config = config
        self.table = table
        self.current_turn = 0
        self.drones: List[Drone] = []

    def run(self, visualizer: Visualizer) -> None:
        """
      Starts the simulation loop, logging outputs and updating the UI.

      Args:
          visualizer (Visualizer): The Tkinter GUI handler for rendering.

      Raises:
          FlyInError: If the engine is initialized with zero drones.
        """
        if not self.drones:
            raise FlyInError("Simulation engine received 0 drones. Aborting.")
        visualizer.draw_map()
        time.sleep(1.5)

        while not self._all_drones_delivered() and visualizer.running:
            self.current_turn += 1
            turn_movements = self._execute_turn()

            if turn_movements:
                self._display_output(turn_movements)
                visualizer.render_turn(turn_movements, self.current_turn)
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
