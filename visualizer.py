import tkinter as tk
from parser import MapConfig
from typing import Dict, List, Tuple


class Visualizer:
    def __init__(self, config: MapConfig,
                 width: int = 800, height: int = 600) -> None:
        self.config = config
        self.width = width
        self.height = height
        self.padding = 50

        self.root = tk.Tk()
        self.root.title("Fly-in Simulation")
        self.canvas = tk.Canvas(self.root, width=width,
                                height=height, bg="#2c3e50")
        self.canvas.pack()

        self.drone_markers: Dict[str, int] = {}
        self.zone_coords: Dict[str, Tuple[float, float]] = {}

        self._calculate_scaling()

    def _calculate_scaling(self) -> None:
        """Determines how to map zone coordinates to screen pixels."""
        all_x = [z.x for z in self.config.zones.values()]
        all_y = [z.y for z in self.config.zones.values()]

        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)

        range_x = max_x - min_x if max_x != min_x else 1
        range_y = max_y - min_y if max_y != min_y else 1

        self.scale_x = (self.width - 2 * self.padding) / range_x
        self.scale_y = (self.height - 2 * self.padding) / range_y
        self.min_x, self.min_y = min_x, min_y

    def _to_pixels(self, x: int, y: int) -> Tuple[float, float]:
        px = self.padding + (x - self.min_x) * self.scale_x
        py = self.height - (self.padding + (y - self.min_y) * self.scale_y)

        return px, py

    def draw_map(self) -> None:
        for zone_name, connections in self.config.graph.items():
            start_px = self._to_pixels(
                self.config.zones[zone_name].x, self.config.zones[zone_name].y)
            for conn in connections:
                target_zone = (conn.zone_b if conn.zone_a.name == zone_name
                               else conn.zone_a)
                end_px = self._to_pixels(target_zone.x, target_zone.y)
                self.canvas.create_line(
                    start_px, end_px, fill="#7f8c8d", width=2)

        for name, zone in self.config.zones.items():
            px, py = self._to_pixels(zone.x, zone.y)
            self.zone_coords[name] = (px, py)

            color = zone.color if zone.color else self._get_type_color(
                zone.zone_type)

            radius = 15
            self.canvas.create_oval(
                px-radius, py-radius, px+radius, py+radius, fill=color,
                outline="white", width=2)
            self.canvas.create_text(
                px, py+25, text=name, fill="white", font=("Arial", 8))

    def _get_type_color(self, zone_type: str) -> str:
        types = {"priority": "#2ecc71",
                 "restricted": "#e74c3c", "blocked": "#95a5a6"}
        return types.get(zone_type, "#3498db")

    def render_turn(self, movements: List[str]) -> None:
        for move in movements:

            parts = move.split('-')
            drone_name = parts[0]

            if len(parts) == 2:
                target_px = self.zone_coords[parts[1]]
            else:
                z1, z2 = self.zone_coords[parts[1]], self.zone_coords[parts[2]]
                target_px = ((z1[0] + z2[0]) / 2, (z1[1] + z2[1]) / 2)

            if drone_name not in self.drone_markers:
                r = 8
                self.drone_markers[drone_name] = self.canvas.create_oval(
                    target_px[0]-r, target_px[1]-r, target_px[0]+r,
                    target_px[1]+r, fill="yellow", outline="black")
                self.canvas.create_text(
                    target_px[0], target_px[1], text=drone_name,
                    font=("Arial", 6))

            else:
                r = 8
                self.canvas.coords(
                    self.drone_markers[drone_name], target_px[0]-r,
                    target_px[1]-r, target_px[0]+r, target_px[1] + r)

        self.root.update()
