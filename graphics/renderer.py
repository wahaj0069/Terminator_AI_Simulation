
import random
from config import GRID_ROWS, GRID_COLS, CELL_SIZE, COLORS


class CityRenderer:
    def __init__(self, canvas, environment):
        self.canvas = canvas
        self.environment = environment
        self.random = random.Random(42)

    def rect(self, x1, y1, x2, y2, color, outline="", width=1):
        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=color,
            outline=outline,
            width=width,
            tags="world"
        )

    def oval(self, x1, y1, x2, y2, color, outline="", width=1):
        self.canvas.create_oval(
            x1, y1, x2, y2,
            fill=color,
            outline=outline,
            width=width,
            tags="world"
        )

    def line(self, x1, y1, x2, y2, color, width=1):
        self.canvas.create_line(
            x1, y1, x2, y2,
            fill=color,
            width=width,
            tags="world"
        )

    def text(self, x, y, value, color="white", size=12):
        self.canvas.create_text(
            x, y,
            text=value,
            fill=color,
            font=("Consolas", size, "bold"),
            tags="world"
        )

    def draw(self):
        self.canvas.delete("world")
        self.draw_ground()
        self.draw_roads()
        self.draw_buildings()
        self.draw_park()
        self.draw_safe_zone()
        self.draw_hazards()
        self.draw_trees()
        self.draw_streetlights()
        self.draw_vehicles()

    def draw_ground(self):
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                tile = self.environment.get_tile(row, col)
                x = col * CELL_SIZE
                y = row * CELL_SIZE

                color = COLORS.get(
                    tile,
                    COLORS["grass"]
                )

                if tile == "building":
                    color = "#345c3d"

                if tile == "obstacle":
                    color = "#303640"

                self.rect(
                    x, y,
                    x + CELL_SIZE,
                    y + CELL_SIZE,
                    color
                )

                if tile == "sidewalk":
                    self.line(
                        x, y,
                        x + CELL_SIZE, y,
                        "#a4aaa8"
                    )

                    self.line(
                        x, y,
                        x, y + CELL_SIZE,
                        "#737b7c"
                    )

                elif tile == "ground":
                    if (row * 7 + col * 11) % 9 == 0:
                        self.rect(
                            x + 8, y + 12,
                            x + 11, y + 16,
                            "#47754a"
                        )

    def draw_roads(self):
        horizontal = [(10, 13), (23, 25)]
        vertical = [(13, 16), (29, 32)]

        world_width = GRID_COLS * CELL_SIZE
        world_height = GRID_ROWS * CELL_SIZE

        for top, bottom in horizontal:
            y1 = top * CELL_SIZE
            y2 = (bottom + 1) * CELL_SIZE

            self.rect(
                0, y1,
                world_width, y2,
                "#303640"
            )

            middle = (y1 + y2) / 2

            for x in range(12, world_width, 72):
                self.rect(
                    x, middle - 2,
                    x + 34, middle + 2,
                    "#d5d4c5"
                )

            self.line(
                0, y1 + 3,
                world_width, y1 + 3,
                "#555b62", 2
            )

            self.line(
                0, y2 - 3,
                world_width, y2 - 3,
                "#555b62", 2
            )

        for left, right in vertical:
            x1 = left * CELL_SIZE
            x2 = (right + 1) * CELL_SIZE

            self.rect(
                x1, 0,
                x2, world_height,
                "#303640"
            )

            middle = (x1 + x2) / 2

            for y in range(12, world_height, 72):
                self.rect(
                    middle - 2, y,
                    middle + 2, y + 34,
                    "#d5d4c5"
                )

            self.line(
                x1 + 3, 0,
                x1 + 3, world_height,
                "#555b62", 2
            )

            self.line(
                x2 - 3, 0,
                x2 - 3, world_height,
                "#555b62", 2
            )

        for top, bottom in horizontal:
            for left, right in vertical:
                x1 = left * CELL_SIZE
                x2 = (right + 1) * CELL_SIZE
                y1 = top * CELL_SIZE
                y2 = (bottom + 1) * CELL_SIZE

                self.rect(
                    x1, y1, x2, y2,
                    "#303640"
                )

                for i in range(7):
                    px = x1 + 8 + i * 16

                    if px + 9 < x2:
                        self.rect(
                            px, y1 + 6,
                            px + 9, y1 + 30,
                            "#cdd0c8"
                        )

                        self.rect(
                            px, y2 - 30,
                            px + 9, y2 - 6,
                            "#cdd0c8"
                        )

    def draw_buildings(self):
        styles = {
            "Helipad": ("#455165", "#253143"),
            "Residential Building": ("#526075", "#303d50"),
            "Police Station": ("#43536a", "#263a54"),
            "Hospital": ("#637082", "#384657"),
            "Office Building": ("#4c586e", "#2b374b")
        }

        for name, data in self.environment.locations.items():
            if data["type"] != "building":
                continue

            top, left, bottom, right = data["bounds"]

            x1 = left * CELL_SIZE
            y1 = top * CELL_SIZE
            x2 = (right + 1) * CELL_SIZE
            y2 = (bottom + 1) * CELL_SIZE

            roof, inner = styles.get(
                name,
                ("#526075", "#303d50")
            )

            self.rect(
                x1 + 8, y1 + 10,
                x2 + 8, y2 + 10,
                "#17212d"
            )

            self.rect(
                x1, y1, x2, y2,
                "#202b3a", "#111a25", 3
            )

            self.rect(
                x1 + 7, y1 + 7,
                x2 - 7, y2 - 32,
                roof, "#8391a1", 3
            )

            self.rect(
                x1 + 17, y1 + 17,
                x2 - 17, y2 - 46,
                inner, "#273447", 2
            )

            if name == "Helipad":
                self.draw_helipad(x1, y1, x2, y2)

            elif name == "Hospital":
                self.draw_hospital(x1, y1, x2, y2)

            elif name == "Police Station":
                self.draw_police(x1, y1, x2, y2)

            else:
                self.draw_rooftop(x1, y1, x2, y2)

            for wx in range(x1 + 18, x2 - 18, 29):
                self.rect(
                    wx, y2 - 27,
                    wx + 18, y2 - 13,
                    "#f4c16c", "#76562d"
                )

            if name not in ("Hospital", "Police Station"):
                self.text(
                    (x1 + x2) / 2,
                    y2 - 7,
                    name.upper(),
                    "#f2f3f0",
                    10
                )

    def draw_rooftop(self, x1, y1, x2, y2):
        for x in range(x1 + 28, x2 - 25, 57):
            self.rect(
                x + 4, y1 + 30,
                x + 39, y1 + 58,
                "#182533"
            )

            self.rect(
                x, y1 + 25,
                x + 35, y1 + 53,
                "#77899c", "#253244", 2
            )

            self.line(
                x + 8, y1 + 31,
                x + 27, y1 + 31,
                "#a3b0bc", 2
            )

    def draw_helipad(self, x1, y1, x2, y2):
        cx = (x1 + x2) / 2
        cy = (y1 + y2 - 32) / 2

        radius = min(
            (x2 - x1) * 0.33,
            (y2 - y1) * 0.32
        )

        self.oval(
            cx - radius, cy - radius,
            cx + radius, cy + radius,
            "#394253", "#c5c9c9", 5
        )

        self.text(
            cx, cy, "H",
            "#f5b64d", 48
        )

    def draw_hospital(self, x1, y1, x2, y2):
        self.draw_rooftop(x1, y1, x2, y2)

        self.rect(
            x1 + 12, y2 - 76,
            x2 - 12, y2 - 36,
            "#e1e5e5", "#687684", 2
        )

        self.text(
            (x1 + x2) / 2,
            y2 - 56,
            "+ HOSPITAL",
            "#bd3542",
            17
        )

    def draw_police(self, x1, y1, x2, y2):
        self.draw_rooftop(x1, y1, x2, y2)

        self.rect(
            x1 + 13, y2 - 77,
            x2 - 13, y2 - 36,
            "#15538c", "#83a3c2", 2
        )

        self.text(
            (x1 + x2) / 2,
            y2 - 56,
            "POLICE",
            "#f3f5e8",
            17
        )

    def draw_park(self):
        data = self.environment.get_location("Central Park")
        top, left, bottom, right = data["bounds"]

        x1 = left * CELL_SIZE
        y1 = top * CELL_SIZE
        x2 = (right + 1) * CELL_SIZE
        y2 = (bottom + 1) * CELL_SIZE

        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2

        self.rect(
            x1 + 5, y1 + 5,
            x2 - 5, y2 - 5,
            "#39794b", "#789c6e", 3
        )

        self.rect(
            cx - 13, y1 + 6,
            cx + 13, y2 - 6,
            "#9b9b8c"
        )

        self.rect(
            x1 + 6, cy - 13,
            x2 - 6, cy + 13,
            "#9b9b8c"
        )

        self.oval(
            cx - 47, cy - 47,
            cx + 47, cy + 47,
            "#a6a9a3", "#596775", 4
        )

        self.oval(
            cx - 36, cy - 36,
            cx + 36, cy + 36,
            "#267da6", "#a6dcea", 4
        )

        self.oval(
            cx - 15, cy - 15,
            cx + 15, cy + 15,
            "#83d9eb"
        )

        for dx, dy in [
            (-83, -48), (83, -48),
            (-83, 48), (83, 48)
        ]:
            self.draw_tree(cx + dx, cy + dy, 0.65)

    def draw_safe_zone(self):
        data = self.environment.get_location("Safe Zone")
        top, left, bottom, right = data["bounds"]

        x1 = left * CELL_SIZE
        y1 = top * CELL_SIZE
        x2 = (right + 1) * CELL_SIZE
        y2 = (bottom + 1) * CELL_SIZE

        self.rect(
            x1 + 4, y1 + 4,
            x2 - 4, y2 - 4,
            "#147a38", "#91f7a8", 3
        )

        self.rect(
            x1 + 13, y1 + 13,
            x2 - 13, y2 - 13,
            "#1b9b4a", "#b0ffc3", 2
        )

        self.text(
            (x1 + x2) / 2,
            (y1 + y2) / 2,
            "SAFE\nZONE",
            "#e1ffe7",
            12
        )

    def draw_hazards(self):
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                if self.environment.get_tile(row, col) != "hazard":
                    continue

                x = col * CELL_SIZE
                y = row * CELL_SIZE

                self.canvas.create_polygon(
                    x + 16, y + 3,
                    x + 3, y + 29,
                    x + 29, y + 29,
                    fill="#e74646",
                    outline="#75232a",
                    width=2,
                    tags="world"
                )

    def draw_tree(self, x, y, scale=1):
        r = 19 * scale

        self.oval(
            x - r + 4, y - r + 10,
            x + r + 4, y + r + 10,
            "#183e2a"
        )

        self.oval(
            x - r, y - r,
            x + r, y + r,
            "#24643b", "#173d2b", 2
        )

        self.oval(
            x - r * 0.6, y - r * 0.9,
            x + r * 0.5, y + r * 0.2,
            "#3e9250"
        )

    def draw_trees(self):
        positions = [
            (38, 85), (380, 85),
            (380, 250), (38, 250),
            (590, 85), (870, 85),
            (590, 250), (870, 250),
            (1100, 85), (1460, 85),
            (1100, 250), (1460, 250),
            (38, 550), (380, 550),
            (38, 730), (380, 730),
            (1100, 550), (1460, 550),
            (1100, 730), (1460, 730)
        ]

        for x, y in positions:
            row = int(y // CELL_SIZE)
            col = int(x // CELL_SIZE)

            if self.environment.get_tile(row, col) == "ground":
                self.draw_tree(x, y, 0.85)

    def draw_streetlights(self):
        positions = [
            (165, 290), (350, 290),
            (680, 290), (1180, 290),
            (165, 710), (350, 710),
            (680, 710), (1180, 710)
        ]

        for x, y in positions:
            self.rect(
                x - 3, y - 19,
                x + 3, y + 12,
                "#1c2934"
            )

            self.oval(
                x - 7, y - 25,
                x + 7, y - 12,
                "#ffe5a4", "#b58b50", 2
            )

    def draw_vehicles(self):
        for obstacle in self.environment.get_obstacles():
            row = obstacle["row"]
            col = obstacle["col"]
            kind = obstacle["kind"]
            color = obstacle["color"]

            x = (col + 0.5) * CELL_SIZE
            y = (row + 0.5) * CELL_SIZE

            if kind == "barricade":
                self.draw_barricade(x, y)
                continue

            vertical = (
                13 <= col <= 16
                or 29 <= col <= 32
            ) and not (
                10 <= row <= 13
                or 23 <= row <= 25
            )

            if kind == "wreck":
                self.draw_wrecked_car(
                    x, y, color, vertical
                )

            else:
                self.draw_car(
                    x, y, color, vertical, kind
                )

    def draw_car(self, x, y, color, vertical, kind):
        if vertical:
            self.draw_vertical_car(x, y, color, kind)
        else:
            self.draw_horizontal_car(x, y, color, kind)

    def draw_horizontal_car(self, x, y, color, kind):
        self.rect(
            x - 15, y - 9,
            x + 15, y + 11,
            "#151a22"
        )

        self.rect(
            x - 14, y - 11,
            x - 7, y - 7,
            "#0c1017"
        )

        self.rect(
            x + 7, y - 11,
            x + 14, y - 7,
            "#0c1017"
        )

        self.rect(
            x - 14, y + 8,
            x - 7, y + 12,
            "#0c1017"
        )

        self.rect(
            x + 7, y + 8,
            x + 14, y + 12,
            "#0c1017"
        )

        self.rect(
            x - 13, y - 8,
            x + 13, y + 8,
            color, "#18202a", 2
        )

        self.rect(
            x - 5, y - 7,
            x + 6, y + 7,
            "#283d51", "#121b26"
        )

        self.rect(
            x - 3, y - 6,
            x + 4, y + 5,
            "#77a9bd"
        )

        self.line(
            x - 1, y - 6,
            x - 1, y + 6,
            "#1c3446"
        )

        self.rect(
            x + 11, y - 6,
            x + 14, y - 2,
            "#f6e5b3"
        )

        self.rect(
            x + 11, y + 2,
            x + 14, y + 6,
            "#f6e5b3"
        )

        self.rect(
            x - 14, y - 6,
            x - 11, y - 2,
            "#b83e46"
        )

        self.rect(
            x - 14, y + 2,
            x - 11, y + 6,
            "#b83e46"
        )

        if kind == "taxi":
            self.rect(
                x - 3, y - 3,
                x + 4, y + 3,
                "#f5e3a5", "#5b4c28"
            )

            self.text(
                x, y,
                "T",
                "#1d2630", 7
            )

        elif kind == "police_car":
            self.rect(
                x - 10, y - 8,
                x - 7, y + 8,
                "#173e77"
            )

            self.rect(
                x - 2, y - 3,
                x + 2, y,
                "#e53949"
            )

            self.rect(
                x - 2, y,
                x + 2, y + 3,
                "#358df5"
            )

    def draw_vertical_car(self, x, y, color, kind):
        self.rect(
            x - 9, y - 15,
            x + 11, y + 15,
            "#151a22"
        )

        self.rect(
            x - 11, y - 14,
            x - 7, y - 7,
            "#0c1017"
        )

        self.rect(
            x + 8, y - 14,
            x + 12, y - 7,
            "#0c1017"
        )

        self.rect(
            x - 11, y + 7,
            x - 7, y + 14,
            "#0c1017"
        )

        self.rect(
            x + 8, y + 7,
            x + 12, y + 14,
            "#0c1017"
        )

        self.rect(
            x - 8, y - 13,
            x + 8, y + 13,
            color, "#18202a", 2
        )

        self.rect(
            x - 7, y - 5,
            x + 7, y + 6,
            "#283d51", "#121b26"
        )

        self.rect(
            x - 6, y - 3,
            x + 5, y + 4,
            "#77a9bd"
        )

        self.line(
            x - 6, y,
            x + 6, y,
            "#1c3446"
        )

        self.rect(
            x - 6, y - 14,
            x - 2, y - 11,
            "#f6e5b3"
        )

        self.rect(
            x + 2, y - 14,
            x + 6, y - 11,
            "#f6e5b3"
        )

        self.rect(
            x - 6, y + 11,
            x - 2, y + 14,
            "#b83e46"
        )

        self.rect(
            x + 2, y + 11,
            x + 6, y + 14,
            "#b83e46"
        )

        if kind == "taxi":
            self.rect(
                x - 3, y - 3,
                x + 3, y + 4,
                "#f5e3a5", "#5b4c28"
            )

            self.text(
                x, y,
                "T",
                "#1d2630", 7
            )

        elif kind == "police_car":
            self.rect(
                x - 8, y - 10,
                x + 8, y - 7,
                "#173e77"
            )

            self.rect(
                x - 3, y - 2,
                x, y + 2,
                "#e53949"
            )

            self.rect(
                x, y - 2,
                x + 3, y + 2,
                "#358df5"
            )

    def draw_wrecked_car(self, x, y, color, vertical):
        self.draw_car(
            x, y, color, vertical, "wreck"
        )

        if vertical:
            self.line(
                x - 6, y - 8,
                x + 6, y + 8,
                "#161b22", 2
            )

            self.line(
                x + 5, y - 7,
                x - 5, y + 7,
                "#c8d4d9", 2
            )

            self.rect(
                x - 7, y + 9,
                x + 7, y + 12,
                "#3d302d"
            )

        else:
            self.line(
                x - 8, y - 6,
                x + 8, y + 6,
                "#161b22", 2
            )

            self.line(
                x - 7, y + 6,
                x + 7, y - 6,
                "#c8d4d9", 2
            )

            self.rect(
                x + 9, y - 7,
                x + 12, y + 7,
                "#3d302d"
            )

        self.oval(
            x - 5, y - 4,
            x + 3, y + 4,
            "#343d43"
        )

        self.line(
            x - 9, y - 9,
            x - 13, y - 13,
            "#b6a59a", 2
        )

        self.line(
            x + 9, y + 8,
            x + 13, y + 12,
            "#b6a59a", 2
        )

    def draw_barricade(self, x, y):
        self.rect(
            x - 15, y - 4,
            x + 15, y + 9,
            "#161d24"
        )

        self.rect(
            x - 14, y - 7,
            x + 14, y + 5,
            "#e7a13a", "#3b2a21", 2
        )

        for offset in (-10, 0, 10):
            self.canvas.create_polygon(
                x + offset - 4, y + 4,
                x + offset + 1, y - 6,
                x + offset + 6, y - 6,
                x + offset + 1, y + 4,
                fill="#292a2b",
                outline="",
                tags="world"
            )

        self.rect(
            x - 11, y + 5,
            x - 7, y + 13,
            "#66696d"
        )

        self.rect(
            x + 7, y + 5,
            x + 11, y + 13,
            "#66696d"
        )

        self.rect(
            x - 13, y - 10,
            x - 9, y - 6,
            "#ffdf74"
        )

        self.rect(
            x + 9, y - 10,
            x + 13, y - 6,
            "#ffdf74"
        )
