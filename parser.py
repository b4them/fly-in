import re
from typing import Optional

from errors import (DuplicateHubError, InvalidCapacityError,
                    InvalidZoneTypeError, MapParsingError)
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

    def _parse_drone_count(self, data: str, line_nb: int) -> None:
        if self.nb_drones != 0:
            raise MapParsingError(line_nb, "Duplicate nb_drones definition")
        if not data.isdigit() or int(data) <= 0:
            raise MapParsingError(
                line_nb, f"nb_drones must be positive: {data}")
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

    def _parse_zone(self, key: str, data: str, line_nb: int) -> None:
        clean_data, metadata = self._extract_metadata(data)

        parts = clean_data.split()
        if len(parts) != 3:
            raise MapParsingError(line_nb, "Hub requires: <name> <x> <y>")

        name, x_str, y_str, = parts[0], parts[1], parts[2]

        def is_int(s: str) -> bool:
            return s.lstrip('-').isdigit()
        if not (is_int(x_str) and is_int(y_str)):
            raise MapParsingError(
                line_nb, f"Invalid coordinates: {x_str} {y_str}")
        if name in self.zones:
            raise DuplicateHubError(
                f"Line {line_nb}: Zone '{name}' already exists")

        max_drones = int(metadata.get('max_drones', 1))
        if max_drones < 1:
            raise InvalidCapacityError(f"Line {line_nb}: Capacity must be > 0")

        zone_type = metadata.get('zone', 'normal')
        if zone_type not in ("normal", "blocked", "restricted", "priority"):
            raise InvalidZoneTypeError(
                f"Line {line_nb}: Unknown type '{zone_type}'")

        new_zone = Zone(name=name, x=int(x_str), y=int(y_str),
                        zone_type=zone_type, color=metadata.get('color'),
                        max_drones=max_drones)

        if key == "start_hub":
            if self.start_hub is not None:
                raise DuplicateHubError(
                    f"Line {line_nb}: Only one start_hub allowed")
            self.start_hub = new_zone
        elif key == "end_hub":
            if self.end_hub is not None:
                raise DuplicateHubError(
                    f"Line {line_nb}: Only one end_hub allowed")
            self.end_hub = new_zone

        self.zones[name] = new_zone
        self.graph[name] = []

    def _parse_connection(self, data: str, line_nb: int) -> None:
        clean_data, metadata = self._extract_metadata(data)

        parts = clean_data.split('-')
        if len(parts) != 2:
            raise MapParsingError(line_nb, "Connection format: zone1-zone2")

        name_a, name_b = parts[0].strip(), parts[1].strip()

        if name_a not in self.zones or name_b not in self.zones:
            raise MapParsingError(
                line_nb, f"Undefined zone in connection: {name_a}-{name_b}")

        if name_a == name_b:
            raise MapParsingError(
                line_nb, "Self-connecting zones are forbidden")

        for existing_conn in self.graph[name_a]:
            if (existing_conn.zone_a.name == name_b
                    or existing_conn.zone_b.name == name_b):
                raise MapParsingError(
                    line_nb, f"Duplicate connection: {name_a}-{name_b}")

        capacity = int(metadata.get('max_link_capacity', 1))
        if capacity < 1:
            raise InvalidCapacityError(
                f"Line {line_nb}: Link capacity must be > 0")

        zone_a = self.zones[name_a]
        zone_b = self.zones[name_b]

        if zone_a.zone_type == "blocked" or zone_b.zone_type == "blocked":
            return

        new_conn = Connection(zone_a=zone_a, zone_b=zone_b, max=capacity)

        self.graph[name_a].append(new_conn)
        self.graph[name_b].append(new_conn)

    def _process_line(self, line: str, line_nb: int) -> None:
        separator = line.find(":")
        if separator == -1:
            raise MapParsingError(line_nb, "Missing colon separator")

        key, value = line[:separator].strip(), line[separator + 1:].strip()

        if key == "nb_drones":
            self._parse_drone_count(value, line_nb)
        elif key in ("start_hub", "end_hub", "hub"):
            self._parse_zone(key, value, line_nb)
        elif key == "connection":
            self._parse_connection(value, line_nb)
        else:
            raise MapParsingError(line_nb, f"Unknown configuration key: {key}")

    @classmethod
    def readfile(cls, filepath: str) -> 'MapConfig':
        config = cls()
        with open(filepath, 'r') as file:
            for line_nb, raw_line in enumerate(file, start=1):
                clean_line = config._clean_line(raw_line)
                if not clean_line:
                    continue
                config._process_line(clean_line, line_nb)

        return config
