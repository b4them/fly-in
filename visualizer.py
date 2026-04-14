import tkinter as tk
from typing import Dict, List
from .parser import MapConfig
from .types import Drone, Zone


class Visualizer:
    def __init__(self, config: MapConfig,
                 width: int = 800, height: int = 600) -> None:
        self.config = config
        self.root = tk.Tk()
        self.root.title("Fly-in Simulation")
        self.canvas = tk.Canvas(self.root, width=width,
                                height=height, bg="white")
        self.canvas.pack()

        self.drone_markers: Dict[str, int] = {}

    def draw_map(self) -> None:
        pass

    def update_drone_position(self, drone_name: str, target_name: str) -> None:
        pass

    def refresh(self) -> None:
        self.root.update()
