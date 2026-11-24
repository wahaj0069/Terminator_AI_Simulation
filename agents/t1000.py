
import random

from agents.base_agent import BaseAgent
from config import (
    T1000_HEALTH,
    T1000_SPEED,
    T1000_VISION,
    T1000_DAMAGE,
    MAX_ENERGY
)


class T1000(BaseAgent):
    def __init__(self, row, col):
        super().__init__(
            name="T-1000",
            agent_type="t1000",
            row=row,
            col=col,
            health=T1000_HEALTH,
            energy=MAX_ENERGY,
            speed=T1000_SPEED,
            vision=T1000_VISION,
            damage=T1000_DAMAGE
        )

        self.state = "searching"
        self.primary_target = None
        self.current_target = None

        self.last_known_position = None
        self.target_visible = False

        self.attack_range = 1
        self.attacks_made = 0
        self.successful_hits = 0
        self.targets_detected = 0
        self.search_steps = 0
        self.chase_steps = 0

        self.patrol_points = []
        self.patrol_index = 0

        self.random = random.Random()

    def assign_target(self, agent):
        self.primary_target = agent
        self.current_target = agent

    def detect_targets(self, agents):
        detected = []

        for agent in agents:
            if not agent.alive:
                continue

            if agent.agent_type not in ("john", "sarah"):
                continue

            if self.can_see(agent):
                detected.append(agent)

        if detected:
            if self.primary_target in detected:
                target = self.primary_target
            else:
                target = min(
                    detected,
                    key=lambda agent: self.distance_to(agent)
                )

            if not self.target_visible:
                self.targets_detected += 1

            self.current_target = target
            self.last_known_position = target.get_position()
            self.target_visible = True

            self.set_state("pursuing")

        else:
            self.target_visible = False
            self.current_target = None

        return detected

    def choose_move_towards(self, position, environment):
        neighbors = environment.get_neighbors(
            self.row,
            self.col
        )

        if not neighbors:
            return None

        target_row, target_col = position

        current_distance = (
            (self.row - target_row) ** 2
            + (self.col - target_col) ** 2
        )

        best_position = min(
            neighbors,
            key=lambda cell: (
                (cell[0] - target_row) ** 2
                + (cell[1] - target_col) ** 2
            )
        )

        new_distance = (
            (best_position[0] - target_row) ** 2
            + (best_position[1] - target_col) ** 2
        )

        if new_distance >= current_distance:
            return None

        return best_position

    def move_towards(self, position, environment):
        if not self.alive:
            return False

        next_position = self.choose_move_towards(
            position,
            environment
        )

        if next_position is None:
            return False

        row, col = next_position

        return self.move(
            row - self.row,
            col - self.col,
            environment
        )

    def pursue_target(self, environment):
        target = self.current_target

        if target is None or not target.alive:
            return False

        self.set_state("pursuing")

        if self.distance_to(target) <= self.attack_range:
            return self.attack_target()

        moved = self.move_towards(
            target.get_position(),
            environment
        )

        if moved:
            self.chase_steps += 1

        return moved

    def attack_target(self):
        target = self.current_target

        if target is None or not target.alive:
            return False

        if self.distance_to(target) > self.attack_range:
            return False

        self.set_state("attacking")

        if self.attack(target):
            self.attacks_made += 1
            self.successful_hits += 1
            return True

        return False

    def search_last_position(self, environment):
        if self.last_known_position is None:
            return False

        if self.get_position() == self.last_known_position:
            self.last_known_position = None
            return False

        self.set_state("investigating")

        moved = self.move_towards(
            self.last_known_position,
            environment
        )

        if moved:
            self.search_steps += 1

        return moved

    def set_patrol_points(self, points):
        self.patrol_points = list(points)
        self.patrol_index = 0

    def patrol(self, environment):
        if not self.patrol_points:
            return self.wander(environment)

        self.set_state("patrolling")

        destination = self.patrol_points[
            self.patrol_index
        ]

        if self.get_position() == destination:
            self.patrol_index = (
                self.patrol_index + 1
            ) % len(self.patrol_points)

            destination = self.patrol_points[
                self.patrol_index
            ]

        moved = self.move_towards(
            destination,
            environment
        )

        if moved:
            self.search_steps += 1

        return moved

    def wander(self, environment):
        if not self.alive:
            return False

        neighbors = environment.get_neighbors(
            self.row,
            self.col
        )

        if not neighbors:
            return False

        self.set_state("searching")

        row, col = self.random.choice(neighbors)

        moved = self.move(
            row - self.row,
            col - self.col,
            environment
        )

        if moved:
            self.search_steps += 1

        return moved

    def decide_action(self, agents, environment):
        if not self.alive:
            return "dead"

        self.detect_targets(agents)

        if self.current_target is not None:
            self.pursue_target(environment)
            return self.state

        if self.last_known_position is not None:
            if self.search_last_position(environment):
                return self.state

        if self.patrol_points:
            self.patrol(environment)
        else:
            self.wander(environment)

        return self.state

    def get_status(self):
        status = super().get_status()

        status.update({
            "primary_target": (
                self.primary_target.name
                if self.primary_target is not None
                else None
            ),
            "current_target": (
                self.current_target.name
                if self.current_target is not None
                else None
            ),
            "target_visible": self.target_visible,
            "last_known_position": self.last_known_position,
            "attacks_made": self.attacks_made,
            "successful_hits": self.successful_hits,
            "targets_detected": self.targets_detected,
            "search_steps": self.search_steps,
            "chase_steps": self.chase_steps
        })

        return status
