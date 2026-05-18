import sys
from parser import MapConfig

from algo import SpaceTime
from engine import SimulationEngine
from errors import FlyInError, display_error
from models import Drone
from traffic import ReservationTable
from visualizer import Visualizer


def main() -> None:
    if len(sys.argv) != 2:
        display_error("Usage: python3 main.py <map_file>")
        sys.exit(1)

    map_path = sys.argv[1]

    try:
        config = MapConfig.readfile(map_path)

        if config.start_hub is None or config.end_hub is None:
            raise FlyInError(
                "Map Error: must define exactly one start_hub and end_hub")

        if not config.is_connected():
            raise FlyInError(
                "Map Error: No valid path exists between start and end.")
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

    except FileNotFoundError:
        display_error(f"File not found: {map_path}")
        sys.exit(1)
    except FlyInError as e:
        display_error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")
        sys.exit(0)
    except Exception as e:
        display_error(f"An unexpected system error occured: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
