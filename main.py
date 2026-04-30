import sys
from parser import MapConfig

from algo import SpaceTime
from engine import SimulationEngine
from models import Drone
from traffic import ReservationTable
from visualizer import Visualizer


def main():
    if len(sys.argv) == 2:
        map_path = sys.argv[1]
    else:
        raise Exception("Provide a map file!")

    config = MapConfig.readfile(map_path)

    if config.start_hub is None or config.end_hub is None:
        print("Error: Start or End hub not defined in map!")
        return

    drones = [Drone(i + 1) for i in range(config.nb_drones)]

    table = ReservationTable(config.start_hub.name, config.end_hub.name)
    solver = SpaceTime(config, table)

    print(f"Planning paths for {config.nb_drones} drones...")
    try:
        solver.solve(drones)
    except ValueError as e:
        print(f"Solver Error: {e}")
        return

    viz = Visualizer(config)
    engine = SimulationEngine(config, table)
    engine.drones = drones

    print("Starting Simulation...")
    engine.run(viz)
    print("Simulation Finished.")

    if viz.running:
        viz.root.mainloop()


if __name__ == "__main__":
    main()
