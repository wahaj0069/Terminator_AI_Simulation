
from world.grid import Grid


class Environment:
    def __init__(self):
        self.grid = Grid()
        self.locations = {}
        self.obstacles = []
        self.generate_city()

    def fill_area(self, top, left, bottom, right, tile):
        for row in range(top, bottom + 1):
            for col in range(left, right + 1):
                self.grid.set_cell(row, col, tile)

    def add_building(self, name, top, left, bottom, right):
        self.fill_area(top, left, bottom, right, "building")

        self.locations[name] = {
            "type": "building",
            "bounds": (top, left, bottom, right)
        }

    def add_location(self, name, tile, top, left, bottom, right):
        self.fill_area(top, left, bottom, right, tile)

        self.locations[name] = {
            "type": tile,
            "bounds": (top, left, bottom, right),
            "position": (
                (top + bottom) // 2,
                (left + right) // 2
            )
        }

    def add_obstacle(self, name, row, col, kind, color):
        if self.grid.get_cell(row, col) != "road":
            return False

        if any(
            obstacle["row"] == row
            and obstacle["col"] == col
            for obstacle in self.obstacles
        ):
            return False

        self.grid.set_cell(row, col, "obstacle")

        self.obstacles.append({
            "name": name,
            "row": row,
            "col": col,
            "kind": kind,
            "color": color
        })

        return True

    def generate_city(self):
        self.locations.clear()
        self.obstacles.clear()

        self.fill_area(0, 0, 26, 47, "ground")

        self.fill_area(10, 0, 13, 47, "road")
        self.fill_area(23, 0, 25, 47, "road")

        self.fill_area(0, 13, 26, 16, "road")
        self.fill_area(0, 29, 26, 32, "road")

        self.fill_area(9, 0, 9, 47, "sidewalk")
        self.fill_area(14, 0, 14, 47, "sidewalk")
        self.fill_area(22, 0, 22, 47, "sidewalk")
        self.fill_area(26, 0, 26, 47, "sidewalk")

        self.fill_area(0, 12, 26, 12, "sidewalk")
        self.fill_area(0, 17, 26, 17, "sidewalk")
        self.fill_area(0, 28, 26, 28, "sidewalk")
        self.fill_area(0, 33, 26, 33, "sidewalk")

        self.fill_area(10, 0, 13, 47, "road")
        self.fill_area(23, 0, 25, 47, "road")
        self.fill_area(0, 13, 26, 16, "road")
        self.fill_area(0, 29, 26, 32, "road")

        self.add_building(
            "Helipad", 2, 2, 7, 10
        )

        self.add_building(
            "Residential Building", 2, 19, 7, 26
        )

        self.add_building(
            "Police Station", 2, 35, 7, 44
        )

        self.add_building(
            "Hospital", 16, 2, 20, 10
        )

        self.add_building(
            "Office Building", 16, 35, 20, 43
        )

        self.add_location(
            "Central Park", "park",
            16, 19, 20, 26
        )

        self.add_location(
            "Safe Zone", "safe_zone",
            17, 44, 20, 46
        )

        hazards = [
            (8, 21),
            (21, 37),
            (15, 6)
        ]

        for index, (row, col) in enumerate(
            hazards,
            start=1
        ):
            self.grid.set_cell(
                row,
                col,
                "hazard"
            )

            self.locations[f"Hazard {index}"] = {
                "type": "hazard",
                "position": (row, col)
            }

        self.generate_road_obstacles()

    def generate_road_obstacles(self):
        obstacle_data = [
            ("Abandoned Sedan 1", 10, 8, "car", "#527a98"),
            ("Abandoned Sedan 2", 13, 22, "car", "#a44f4f"),
            ("Damaged Taxi 1", 10, 36, "taxi", "#d9a72e"),
            ("Police Car 1", 13, 42, "police_car", "#e5e8ef"),

            ("Abandoned Sedan 3", 23, 5, "car", "#667f69"),
            ("Damaged Taxi 2", 25, 20, "taxi", "#d2a12d"),
            ("Abandoned Sedan 4", 23, 37, "car", "#8a5c72"),
            ("Police Car 2", 25, 44, "police_car", "#d8e1ea"),

            ("Wrecked Car 1", 4, 13, "wreck", "#8a493d"),
            ("Abandoned Sedan 5", 7, 16, "car", "#3f7e89"),
            ("Wrecked Car 2", 17, 13, "wreck", "#76635b"),
            ("Abandoned Sedan 6", 20, 16, "car", "#a2784d"),

            ("Abandoned Sedan 7", 3, 29, "car", "#5a7a9d"),
            ("Wrecked Car 3", 7, 32, "wreck", "#995947"),
            ("Abandoned Sedan 8", 17, 29, "car", "#628b70"),
            ("Police Car 3", 20, 32, "police_car", "#e0e6ed"),

            ("Road Barricade 1", 11, 25, "barricade", "#e4a13c"),
            ("Road Barricade 2", 24, 34, "barricade", "#e4a13c")
        ]

        for name, row, col, kind, color in obstacle_data:
            self.add_obstacle(
                name,
                row,
                col,
                kind,
                color
            )

    def is_walkable(self, row, col):
        if self.grid.get_cell(row, col) == "obstacle":
            return False

        return self.grid.is_walkable(row, col)

    def get_neighbors(self, row, col):
        neighbors = self.grid.get_neighbors(row, col)

        return [
            position
            for position in neighbors
            if self.is_walkable(*position)
        ]

    def get_tile(self, row, col):
        return self.grid.get_cell(row, col)

    def get_location(self, name):
        return self.locations.get(name)

    def get_obstacles(self):
        return self.obstacles

    def get_obstacle_at(self, row, col):
        for obstacle in self.obstacles:
            if (
                obstacle["row"] == row
                and obstacle["col"] == col
            ):
                return obstacle

        return None
