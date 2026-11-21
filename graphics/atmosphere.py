
import math
import random

from config import (
    CELL_SIZE,
    GRID_ROWS,
    GRID_COLS,
    WORLD_WIDTH,
    WORLD_HEIGHT
)


class AtmosphereParticle:
    def __init__(self, x, y, particle_type, rng):
        self.x = float(x)
        self.y = float(y)
        self.particle_type = particle_type

        self.age = rng.uniform(0, 10)
        self.phase = rng.uniform(0, math.tau)

        if particle_type == "dust":
            self.speed_x = rng.uniform(-5, 5)
            self.speed_y = rng.uniform(-10, -3)
            self.radius = rng.uniform(0.6, 1.5)
            self.color = "#a8b5aa"

        elif particle_type == "ember":
            self.speed_x = rng.uniform(-7, 7)
            self.speed_y = rng.uniform(-20, -8)
            self.radius = rng.uniform(1.0, 2.1)
            self.color = "#ff9852"

        else:
            self.speed_x = rng.uniform(-3, 3)
            self.speed_y = rng.uniform(-5, -1)
            self.radius = rng.uniform(0.8, 1.8)
            self.color = "#a7dfff"

    def update(self, delta_time):
        self.age += delta_time

        self.x += (
            self.speed_x
            + math.sin(self.age * 0.8 + self.phase) * 2
        ) * delta_time

        self.y += self.speed_y * delta_time

        if self.x < 0:
            self.x += WORLD_WIDTH

        if self.x > WORLD_WIDTH:
            self.x -= WORLD_WIDTH

        if self.y < 0:
            self.y += WORLD_HEIGHT

        if self.y > WORLD_HEIGHT:
            self.y -= WORLD_HEIGHT


class CityAtmosphere:
    def __init__(self, environment):
        self.environment = environment
        self.random = random.Random(9201)

        self.time = 0.0
        self.particles = []
        self.streetlights = []
        self.hazard_lights = []
        self.reflections = []

        self.enabled = True
        self.particle_count = 65

        self.generate()

    def generate(self):
        self.particles.clear()
        self.streetlights.clear()
        self.hazard_lights.clear()
        self.reflections.clear()

        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                tile = self.environment.get_tile(row, col)

                x = (col + 0.5) * CELL_SIZE
                y = (row + 0.5) * CELL_SIZE

                if tile == "sidewalk":
                    if (
                        row % 5 == 0
                        and col % 6 == 0
                    ):
                        self.streetlights.append({
                            "x": x,
                            "y": y,
                            "phase": self.random.uniform(
                                0, math.tau
                            )
                        })

                if tile == "hazard":
                    self.hazard_lights.append({
                        "x": x,
                        "y": y,
                        "phase": self.random.uniform(
                            0, math.tau
                        )
                    })

                if tile == "road":
                    if self.random.random() < 0.065:
                        self.reflections.append({
                            "x": x,
                            "y": y,
                            "length": self.random.uniform(
                                8, 22
                            ),
                            "phase": self.random.uniform(
                                0, math.tau
                            )
                        })

        for _ in range(self.particle_count):
            x = self.random.uniform(
                0, WORLD_WIDTH
            )

            y = self.random.uniform(
                0, WORLD_HEIGHT
            )

            particle_type = self.random.choices(
                ["dust", "ember", "mist"],
                weights=[65, 10, 25],
                k=1
            )[0]

            self.particles.append(
                AtmosphereParticle(
                    x,
                    y,
                    particle_type,
                    self.random
                )
            )

    def reset(self):
        self.time = 0.0
        self.generate()

    def update(self, delta_time):
        if not self.enabled:
            return

        self.time += delta_time

        for particle in self.particles:
            particle.update(delta_time)

    def draw_glow(
        self,
        canvas,
        x,
        y,
        radius,
        color,
        scale
    ):
        outer = radius * scale

        canvas.create_oval(
            x - outer,
            y - outer,
            x + outer,
            y + outer,
            fill=color,
            outline="",
            stipple="gray12",
            tags="dynamic"
        )

        inner = outer * 0.45

        canvas.create_oval(
            x - inner,
            y - inner,
            x + inner,
            y + inner,
            fill=color,
            outline="",
            stipple="gray25",
            tags="dynamic"
        )

    def draw_streetlights(
        self,
        canvas,
        world_to_screen,
        scale
    ):
        for light in self.streetlights:
            x, y = world_to_screen(
                light["x"],
                light["y"]
            )

            pulse = (
                0.92
                + math.sin(
                    self.time * 1.8
                    + light["phase"]
                ) * 0.08
            )

            self.draw_glow(
                canvas,
                x,
                y,
                21 * pulse,
                "#ffd36e",
                scale
            )

            radius = max(1.5, 3 * scale)

            canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill="#fff1ad",
                outline="#c68c40",
                tags="dynamic"
            )

    def draw_hazard_lights(
        self,
        canvas,
        world_to_screen,
        scale
    ):
        for hazard in self.hazard_lights:
            x, y = world_to_screen(
                hazard["x"],
                hazard["y"]
            )

            pulse = (
                0.65
                + (
                    math.sin(
                        self.time * 4
                        + hazard["phase"]
                    ) + 1
                ) * 0.3
            )

            self.draw_glow(
                canvas,
                x,
                y,
                25 * pulse,
                "#ff4938",
                scale
            )

            radius = max(
                1,
                3.5 * pulse * scale
            )

            canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill="#ffb15d",
                outline="",
                tags="dynamic"
            )

    def draw_reflections(
        self,
        canvas,
        world_to_screen,
        scale
    ):
        for reflection in self.reflections:
            x, y = world_to_screen(
                reflection["x"],
                reflection["y"]
            )

            pulse = (
                math.sin(
                    self.time * 1.4
                    + reflection["phase"]
                ) + 1
            ) / 2

            length = (
                reflection["length"]
                * scale
            )

            canvas.create_line(
                x - length / 2,
                y,
                x + length / 2,
                y,
                fill=(
                    "#687e8d"
                    if pulse > 0.5
                    else "#465867"
                ),
                width=max(1, scale),
                tags="dynamic"
            )

    def draw_particles(
        self,
        canvas,
        world_to_screen,
        scale
    ):
        for particle in self.particles:
            x, y = world_to_screen(
                particle.x,
                particle.y
            )

            radius = max(
                0.5,
                particle.radius * scale
            )

            if particle.particle_type == "ember":
                pulse = (
                    math.sin(
                        particle.age * 5
                        + particle.phase
                    ) + 1
                ) / 2

                radius *= 0.7 + pulse * 0.6

            canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill=particle.color,
                outline="",
                tags="dynamic"
            )

    def draw(
        self,
        canvas,
        world_to_screen,
        scale
    ):
        if not self.enabled:
            return

        self.draw_reflections(
            canvas,
            world_to_screen,
            scale
        )

        self.draw_streetlights(
            canvas,
            world_to_screen,
            scale
        )

        self.draw_hazard_lights(
            canvas,
            world_to_screen,
            scale
        )

        self.draw_particles(
            canvas,
            world_to_screen,
            scale
        )

    def get_statistics(self):
        return {
            "enabled": self.enabled,
            "particles": len(self.particles),
            "streetlights": len(self.streetlights),
            "hazards": len(self.hazard_lights),
            "reflections": len(self.reflections)
        }
