
import math

from config import CELL_SIZE


class MovementController:
    def __init__(self, environment):
        self.environment = environment

        self.positions = {}
        self.velocities = {}
        self.directions = {}
        self.moving = {}

        self.radius = CELL_SIZE * 0.24
        self.speed_scale = CELL_SIZE * 2.2

    def register_agent(self, agent):
        x = (agent.col + 0.5) * CELL_SIZE
        y = (agent.row + 0.5) * CELL_SIZE

        self.positions[agent] = (float(x), float(y))
        self.velocities[agent] = (0.0, 0.0)
        self.directions[agent] = 0.0
        self.moving[agent] = False

    def register_agents(self, agents):
        for agent in agents:
            self.register_agent(agent)

    def reset(self, agents):
        self.positions.clear()
        self.velocities.clear()
        self.directions.clear()
        self.moving.clear()

        self.register_agents(agents)

    def get_position(self, agent):
        if agent not in self.positions:
            self.register_agent(agent)

        return self.positions[agent]

    def get_velocity(self, agent):
        return self.velocities.get(agent, (0.0, 0.0))

    def get_direction(self, agent):
        return self.directions.get(agent, 0.0)

    def is_moving(self, agent):
        return self.moving.get(agent, False)

    def get_grid_position(self, agent):
        x, y = self.get_position(agent)

        col = int(x // CELL_SIZE)
        row = int(y // CELL_SIZE)

        return row, col

    def is_position_walkable(self, x, y):
        radius = self.radius

        points = [
            (x - radius, y - radius),
            (x + radius, y - radius),
            (x - radius, y + radius),
            (x + radius, y + radius),
            (x, y - radius),
            (x, y + radius),
            (x - radius, y),
            (x + radius, y)
        ]

        for px, py in points:
            col = math.floor(px / CELL_SIZE)
            row = math.floor(py / CELL_SIZE)

            if not self.environment.is_walkable(row, col):
                return False

        return True

    def set_position(self, agent, x, y):
        if not agent.alive:
            return False

        if not self.is_position_walkable(x, y):
            return False

        self.positions[agent] = (float(x), float(y))

        row, col = self.get_grid_position(agent)

        agent.row = row
        agent.col = col

        return True

    def get_speed(self, agent):
        return max(
            0.0,
            agent.speed * self.speed_scale
        )

    def move(self, agent, dx, dy, delta_time):
        if not agent.alive:
            self.moving[agent] = False
            self.velocities[agent] = (0.0, 0.0)
            return False

        if delta_time <= 0:
            return False

        magnitude = math.hypot(dx, dy)

        if magnitude < 0.0001:
            self.velocities[agent] = (0.0, 0.0)
            self.moving[agent] = False
            return False

        dx /= magnitude
        dy /= magnitude

        speed = self.get_speed(agent)

        vx = dx * speed
        vy = dy * speed

        self.velocities[agent] = (vx, vy)
        self.directions[agent] = math.degrees(
            math.atan2(dy, dx)
        )

        x, y = self.get_position(agent)

        distance_x = vx * delta_time
        distance_y = vy * delta_time

        distance = math.hypot(
            distance_x,
            distance_y
        )

        max_step = max(
            1.0,
            self.radius * 0.5
        )

        steps = max(
            1,
            math.ceil(distance / max_step)
        )

        step_x = distance_x / steps
        step_y = distance_y / steps

        moved = False

        for _ in range(steps):
            new_x = x + step_x
            new_y = y + step_y

            if self.is_position_walkable(
                new_x, new_y
            ):
                x = new_x
                y = new_y
                moved = True

            else:
                if self.is_position_walkable(
                    new_x, y
                ):
                    x = new_x
                    moved = True

                if self.is_position_walkable(
                    x, new_y
                ):
                    y = new_y
                    moved = True

        if moved:
            self.set_position(agent, x, y)

        self.moving[agent] = moved

        if not moved:
            self.velocities[agent] = (0.0, 0.0)

        return moved

    def move_player(self, agent, keys, delta_time):
        dx = 0
        dy = 0

        if "w" in keys or "up" in keys:
            dy -= 1

        if "s" in keys or "down" in keys:
            dy += 1

        if "a" in keys or "left" in keys:
            dx -= 1

        if "d" in keys or "right" in keys:
            dx += 1

        return self.move(
            agent,
            dx,
            dy,
            delta_time
        )

    def move_towards(
        self,
        agent,
        target_x,
        target_y,
        delta_time,
        stopping_distance=2.0
    ):
        x, y = self.get_position(agent)

        dx = target_x - x
        dy = target_y - y

        distance = math.hypot(dx, dy)

        if distance <= stopping_distance:
            self.stop(agent)
            return True

        speed = self.get_speed(agent)

        if speed <= 0:
            return False

        max_distance = max(
            0.0,
            distance - stopping_distance
        )

        step_time = min(
            delta_time,
            max_distance / speed
        )

        self.move(
            agent,
            dx,
            dy,
            step_time
        )

        x, y = self.get_position(agent)

        remaining = math.hypot(
            target_x - x,
            target_y - y
        )

        return remaining <= stopping_distance

    def stop(self, agent):
        self.velocities[agent] = (0.0, 0.0)
        self.moving[agent] = False

    def get_distance(self, first, second):
        x1, y1 = self.get_position(first)
        x2, y2 = self.get_position(second)

        return math.hypot(
            x2 - x1,
            y2 - y1
        )

    def get_distance_to_point(
        self,
        agent,
        target_x,
        target_y
    ):
        x, y = self.get_position(agent)

        return math.hypot(
            target_x - x,
            target_y - y
        )

    def get_status(self, agent):
        x, y = self.get_position(agent)

        vx, vy = self.get_velocity(agent)

        return {
            "position": (round(x, 2), round(y, 2)),
            "grid_position": self.get_grid_position(agent),
            "velocity": (round(vx, 2), round(vy, 2)),
            "direction": round(
                self.get_direction(agent), 2
            ),
            "moving": self.is_moving(agent),
            "speed": round(
                math.hypot(vx, vy), 2
            )
        }
