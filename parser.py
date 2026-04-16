import re
from typing import Optional

from models import Connection, Zone


class MapConfig:
    def __init__(self) -> None:
        self.nb_drones: int = 0
        self.start_hub: Optional[Zone] = None
        self.end_hub: Optional[Zone] = None
        self.zones: dict[str, Zone] = {}
        self.graph: dict[str, list[Connection]] = {}

    def _clean_line(self, line: str) -> str:
        clean_line = line.strip()
        if not clean_line or clean_line.startswith("#"):
            return ""
        return clean_line

    def _parse_drone_count(self, data: str) -> None:
        if self.nb_drones != 0:
            pass
        if not data.isdigit() or int(data) <= 0:
            pass
        self.nb_drones = int(data)

    def _extract_metadata(self, data: str) -> tuple[str, dict[str, str]]:
        metadata = {}
        match = re.search(r'\[(.*?)\]', data)

        if match:
            raw_meta = match.group(1)
            pairs = re.findall(r'([\w]+)=([\w]+)', raw_meta)
            metadata = dict(pairs)

            data = data[:match.start()].strip()

        return data, metadata

    def _parse_zone(self, key: str, data: str) -> None:
        clean_data, metadata = self._extract_metadata(data)

        parts = clean_data.split()
        if len(parts) != 3:
            pass

        name, x_str, y_str, = parts[0], parts[1], parts[2]

        if not (x_str.isdigit() and y_str.isdigit()):
            pass
        if name in self.zones:
            pass

        max_drones = int(metadata.get('max_drones', 1))
        zone_type = metadata.get('zone', 'normal')
        color = metadata.get('color', None)

        new_zone = Zone(name=name, x=int(x_str), y=int(y_str),
                        zone_type=zone_type, color=color,
                        max_drones=max_drones)

        if key == "start_hub":
            if self.start_hub is not None:
                pass
            self.start_hub = new_zone
        elif key == "end_hub":
            if self.end_hub is not None:
                pass
            self.end_hub = new_zone

        self.zones[name] = new_zone
        self.graph[name] = []

    def _parse_connection(self, data: str) -> None:
        clean_data, metadata = self._extract_metadata(data)

        parts = clean_data.split('-')
        if len(parts) != 2:
            pass
            return

        name_a, name_b = parts[0].strip(), parts[1].strip()

        if name_a not in self.zones or name_b not in self.zones:
            pass
            return

        if name_a == name_b:
            pass
            return

        for existing_conn in self.graph[name_a]:
            if (existing_conn.zone_a.name == name_b
                    or existing_conn.zone_b.name == name_b):
                pass
                return

        capacity = int(metadata.get('max_link_capacity', 1))

        zone_a = self.zones[name_a]
        zone_b = self.zones[name_b]

        new_conn = Connection(zone_a=zone_a, zone_b=zone_b, max=capacity)

        self.graph[name_a].append(new_conn)
        self.graph[name_b].append(new_conn)

    def _process_line(self, line: str) -> None:
        separator = line.find(":")

        # if separator = -1

        key = line[:separator].strip()
        value = line[separator + 1:].strip()

        # if duplicate

        if key == "nb_drones":
            self._parse_drone_count(value)
        elif key in ("start_hub", "end_hub", "hub"):
            self._parse_zone(key, value)
        elif key == "connection":
            self._parse_connection(value)
        else:
            pass

    @classmethod
    def readfile(cls, filepath: str) -> 'MapConfig':
        config = cls()
        with open(filepath, 'r') as file:
            for line_nb, raw_line in enumerate(file, start=1):
                try:
                    clean_line = config._clean_line(raw_line)
                    if not clean_line:
                        continue
                    config._process_line(clean_line)

                except ValueError as e:
                    print(f"Parsing Error on line {line_nb}: {e}")

        return config
