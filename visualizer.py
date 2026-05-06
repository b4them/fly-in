import time
import tkinter as tk
from parser import MapConfig
from typing import Any, Dict, List, Optional, Tuple

from errors import FlyInError


class Visualizer:
    def __init__(self, config: MapConfig,
                 width: int = 1200, height: int = 800) -> None:
        self.config = config
        self.width = width
        self.height = height
        self.padding = 100
        self.running = True
        self.paused = False

        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.title("Fly-in Simulation")
        self.canvas = tk.Canvas(self.root, width=width,
                                height=height, bg="#2c3e50")
        self.canvas.pack()

        self.root.bind("<space>", self.toggle_pause)
        self.root.bind("<Escape>", self.on_close)
        self.drone_texts: Dict[str, int] = {}
        self.drone_markers: Dict[str, int] = {}
        self.zone_coords: Dict[str, Tuple[float, float]] = {}
        self.drone_positions: Dict[str, Tuple[float, float]] = {}

        self.bg_img: Optional[tk.PhotoImage] = None
        self.drone_img: Optional[tk.PhotoImage] = None
        self.start_img: Optional[tk.PhotoImage] = None
        self.goal_img: Optional[tk.PhotoImage] = None

        self._load_images()
        self._calculate_scaling()

        self._calculate_scaling()

        self.turn_text = self.canvas.create_text(
            30, 30,
            text="Turn: 0",
            fill="#ecf0f1",
            font=("Arial", 16, "bold"),
            anchor="nw"
        )

    def _load_images(self) -> None:
        """Attempts to load PNG assets. Fails silently to fallback shapes."""
        try:
            self.bg_img = tk.PhotoImage(file="assets/bg.png")
        except tk.TclError:
            pass

        try:
            self.drone_img = tk.PhotoImage(file="assets/drone.png")
        except tk.TclError:
            pass

        try:
            self.start_img = tk.PhotoImage(file="assets/start.png")
        except tk.TclError:
            pass

        try:
            self.goal_img = tk.PhotoImage(file="assets/goal.png")
        except tk.TclError:
            pass

    def toggle_pause(self, event: Any) -> None:
        self.paused = not self.paused

    def _calculate_scaling(self) -> None:
        """Determines how to map zone coordinates to screen pixels."""

        self.padding = 60 if len(self.config.zones) < 10 else 120

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

        if self.bg_img:
            self.canvas.create_image(self.width / 2,
                                     self.height / 2, image=self.bg_img
                                     )
        for zone_name, connections in self.config.graph.items():
            start_px = self._to_pixels(
                self.config.zones[zone_name].x, self.config.zones[zone_name].y)
            for conn in connections:
                target_zone = (conn.zone_b if conn.zone_a.name == zone_name
                               else conn.zone_a)
                end_px = self._to_pixels(target_zone.x, target_zone.y)
                self.canvas.create_line(
                    start_px, end_px, fill="#7f8c8d", width=1)

        for i, (name, zone) in enumerate(self.config.zones.items()):
            px, py = self._to_pixels(zone.x, zone.y)
            self.zone_coords[name] = (px, py)

            offset = 25 if i % 2 == 0 else -25

            if self.config.start_hub and name == self.config.start_hub.name and self.start_img:
                self.canvas.create_image(px, py, image=self.start_img)

            elif self.config.end_hub and name == self.config.end_hub.name and self.goal_img:
                self.canvas.create_image(px, py, image=self.goal_img)

            else:
                color = self._parse_color(
                    zone.color, self._get_type_color(zone.zone_type))
                radius = 12
                try:
                    self.canvas.create_oval(px-radius, py-radius,
                                            px+radius, py+radius,
                                            fill=color, outline="white", width=2)
                except tk.TclError:
                    self.canvas.create_oval(px-radius, py-radius,
                                            px+radius, py+radius,
                                            fill="gray", outline="white", width=2)
            self.canvas.create_text(
                px, py + offset,
                text=name,
                fill="#2c3e50",
                font=("Arial", 6, "bold")
            )

        try:
            self.root.lift()
            self.root.update_idletasks()
            self.root.update()
        except tk.TclError:
            self.running = False

    def _parse_color(self, color_name: Optional[str], fallback: str) -> str:
        if not color_name:
            return fallback

        custom_colors = {
            "rainbow": "#ff00ff",
            "darkred": "#8B0000",
            "crimson": "#DC143C",
            "gold": "#FFD700",
            "brown": "#A52A2A",
            "lime": "#00FF00"

        }
        return custom_colors.get(color_name.lower(), color_name)

    def _get_type_color(self, zone_type: str) -> str:
        types = {"priority": "#2ecc71",
                 "restricted": "#e74c3c", "blocked": "#95a5a6"}
        return types.get(zone_type, "#3498db")

    def _prepare_targets(
        self, movements: List[str]
    ) -> Dict[str, Tuple[float, float]]:
        targets: Dict[str, Tuple[float, float]] = {}

        for move in movements:
            parts = move.split('-')
            drone_name = parts[0]

            if len(parts) == 2:
                target_px = self.zone_coords[parts[1]]
            else:
                z1, z2 = self.zone_coords[parts[1]], self.zone_coords[parts[2]]
                target_px = ((z1[0] + z2[0]) / 2, (z1[1] + z2[1]) / 2)

            targets[drone_name] = target_px

            if drone_name not in self.drone_positions:

                s_h_n = (self.config.start_hub.name
                         if self.config.start_hub else parts[1])
                self.drone_positions[drone_name] = self.zone_coords[s_h_n]

                start_px = self.drone_positions[drone_name]

                if self.drone_img:
                    self.drone_markers[drone_name] = self.canvas.create_image(
                        start_px[0], start_px[1],
                        image=self.drone_img, tags="drones")
                else:

                    r = 8
                    self.drone_markers[drone_name] = self.canvas.create_oval(
                        start_px[0]-r, start_px[1]-r, start_px[0]+r,
                        start_px[1]+r, fill="yellow",
                        outline="black", tags="drones")

                self.drone_texts[drone_name] = self.canvas.create_text(
                    start_px[0], start_px[1] - 15,
                    text=drone_name, fill="white",
                    font=("Arial", 8, "bold"),
                    tags="drones")

        return targets

    def _animate_movement(
        self, targets: Dict[str, Tuple[float, float]], steps: int
    ) -> None:

        for s in range(1, steps + 1):
            if not self.running:
                return

            for drone_name, target_px in targets.items():
                start_px = self.drone_positions[drone_name]

                curr_x = start_px[0] + \
                    (target_px[0] - start_px[0]) * (s / steps)
                curr_y = start_px[1] + \
                    (target_px[1] - start_px[1]) * (s / steps)

                if self.drone_img:
                    self.canvas.coords(
                        self.drone_markers[drone_name], curr_x, curr_y)

                else:
                    r = 8
                    self.canvas.coords(
                        self.drone_markers[drone_name], curr_x-r,
                        curr_y-r, curr_x+r, curr_y+r)

                self.canvas.coords(
                    self.drone_texts[drone_name], curr_x, curr_y - 15)

            try:
                self.canvas.tag_raise("drones")
                self.root.update_idletasks()
                self.root.update()
            except tk.TclError:
                self.running = False
                return

            time.sleep(0.02)

    def render_turn(self, movements: List[str],
                    turn: int, steps: int = 20) -> None:
        if not self.running:
            return

        try:
            import time
            while self.paused and self.running:
                self.root.update()
                time.sleep(0.1)
        except tk.TclError:
            self.running = False

        if not self.running:
            return

        try:
            if not self.root.winfo_exists():
                return

            if not self.config.zones:
                raise FlyInError("Visualizer cannot render map with no zones.")

            self.canvas.itemconfig(self.turn_text, text=f"Turn: {turn}")

            targets = self._prepare_targets(movements)

            self._animate_movement(targets, steps)

            for drone_name, target_px in targets.items():
                self.drone_positions[drone_name] = target_px

        except (tk.TclError, SystemExit):
            self.running = False

    def on_close(self, event: Any = None) -> None:
        self.running = False
        try:
            self.root.destroy()
        except tk.TclError:
            pass
