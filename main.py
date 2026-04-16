# Rename 'types_file' to whatever your types file is named
from parser import MapConfig

from engine import SimulationEngine
from models import Drone, Path
from traffic import ReservationTable
from visualizer import Visualizer


def main():
    # 1. Parse the map
    config = MapConfig.readfile("test_map.txt")

    if config.start_hub is None or config.end_hub is None:
        print("Error: Map parsing failed to identify start or end hubs.")
        return
    # 2. Initialize Traffic Table
    # Note: Use the actual names from the parsed hubs
    table = ReservationTable(config.start_hub.name, config.end_hub.name)

    # 3. Initialize Visualizer
    viz = Visualizer(config)

    # 4. Setup Engine
    engine = SimulationEngine(config, table)

    # 5. Create a Mock Drone and Path
    # We manually simulate: Turn 1 -> hubC, Turn 2 -> hubC (restricted cost), Turn 3 -> hubB
    d1 = Drone(1)
    p1 = Path(d1.name, config.end_hub.name)

    # Move D1 from hubA to hubC (Restricted transit)
    # Turn 1: Drone is on the connection
    conn_ac = config.graph[config.start_hub.name][0]
    p1.add_movement(1, conn_ac)

    # Turn 2: Drone arrives at hubC
    p1.add_movement(2, config.zones["hubC"])

    # Turn 3: Drone arrives at hubB (Goal)
    p1.add_movement(3, config.end_hub)

    d1.set_path(p1)
    engine.drones.append(d1)

    # 6. Run the simulation
    print("Starting Mock Simulation...")
    engine.run(viz)
    print("Simulation Finished.")

    # Keep window open
    viz.root.mainloop()


if __name__ == "__main__":
    main()
