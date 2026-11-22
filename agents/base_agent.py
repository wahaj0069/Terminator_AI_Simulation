
import math


class BaseAgent:
    def __init__(
        self,
        name,
        agent_type,
        row,
        col,
        health=100,
        energy=100,
        speed=2.0,
        vision=6,
        damage=0
    ):
        self.name = name
        self.agent_type = agent_type

        self.row = row
        self.col = col

        self.max_health = health
        self.health = health

        self.max_energy = energy
        self.energy = energy

        self.speed = speed
        self.vision = vision
        self.damage = damage

        self.state = "idle"
        self.alive = True

        self.target = None
        self.path = []

        self.total_distance = 0
        self.encounters = 0

    def get_position(self):
        return self.row, self.col

    def set_position(self, row, col, environment):
        if not self.alive:
            return False

        if not environment.is_walkable(row, col):
            return False

        distance = math.dist(
            (self.row, self.col),
            (row, col)
        )

        self.row = row
        self.col = col

        self.total_distance += distance
        return True

    def move(self, dr, dc, environment):
        if not self.alive or self.energy <= 0:
            return False

        new_row = self.row + dr
        new_col = self.col + dc

        if abs(dr) + abs(dc) != 1:
            return False

        if self.set_position(
            new_row,
            new_col,
            environment
        ):
            self.energy = max(
                0,
                self.energy - 1
            )
            return True

        return False

    def distance_to(self, other):
        return math.dist(
            self.get_position(),
            other.get_position()
        )

    def can_see(self, other):
        if not self.alive or not other.alive:
            return False

        return self.distance_to(other) <= self.vision

    def take_damage(self, amount):
        if not self.alive:
            return

        self.health = max(
            0,
            self.health - max(0, amount)
        )

        if self.health == 0:
            self.alive = False
            self.state = "dead"

    def heal(self, amount):
        if not self.alive:
            return

        self.health = min(
            self.max_health,
            self.health + max(0, amount)
        )

    def restore_energy(self, amount):
        if not self.alive:
            return

        self.energy = min(
            self.max_energy,
            self.energy + max(0, amount)
        )

    def attack(self, other):
        if not self.alive or not other.alive:
            return False

        if self.distance_to(other) > 1:
            return False

        if self.damage <= 0:
            return False

        other.take_damage(self.damage)
        self.encounters += 1

        return True

    def set_state(self, state):
        if self.alive:
            self.state = state

    def set_target(self, target):
        self.target = target

    def set_path(self, path):
        self.path = list(path)

    def follow_path(self, environment):
        if not self.path:
            return False

        next_row, next_col = self.path[0]

        dr = next_row - self.row
        dc = next_col - self.col

        if self.move(dr, dc, environment):
            self.path.pop(0)
            return True

        return False

    def get_health_percentage(self):
        return (
            self.health / self.max_health * 100
            if self.max_health > 0 else 0
        )

    def get_energy_percentage(self):
        return (
            self.energy / self.max_energy * 100
            if self.max_energy > 0 else 0
        )

    def get_status(self):
        return {
            "name": self.name,
            "type": self.agent_type,
            "position": self.get_position(),
            "health": self.health,
            "energy": self.energy,
            "state": self.state,
            "alive": self.alive,
            "distance": round(self.total_distance, 2),
            "encounters": self.encounters
        }
