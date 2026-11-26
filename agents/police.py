
import random

from agents.base_agent import BaseAgent
from config import (
    POLICE_HEALTH,
    POLICE_SPEED,
    POLICE_VISION,
    POLICE_DAMAGE,
    MAX_ENERGY
)


class PoliceOfficer(BaseAgent):
    def __init__(self, row, col, officer_id=1):
        super().__init__(
            name=f"Officer {officer_id}",
            agent_type="police",
            row=row,
            col=col,
            health=POLICE_HEALTH,
            energy=MAX_ENERGY,
            speed=POLICE_SPEED,
            vision=POLICE_VISION,
            damage=POLICE_DAMAGE
        )

        self.officer_id = officer_id
        self.state = "patrolling"

        self.patrol_points = []
        self.patrol_index = 0

        self.current_suspect = None
        self.last_known_position = None
        self.incident_location = None

        self.attack_range = 1
        self.alert_level = 0

        self.patrol_steps = 0
        self.investigations = 0
        self.suspects_detected = 0
        self.attacks_made = 0
        self.incidents_resolved = 0

        self.random = random.Random(officer_id)

    def set_patrol_route(self, points):
        self.patrol_points = list(points)
        self.patrol_index = 0

    def detect_suspects(self, agents):
        suspects = []

        for agent in agents:
            if not agent.alive:
                continue

            if agent is self:
                continue

            if agent.agent_type != "t1000":
                continue

            if self.can_see(agent):
                suspects.append(agent)

        if suspects:
            suspect = min(
                suspects,
                key=lambda agent: self.distance_to(agent)
            )

            if self.current_suspect is not suspect:
                self.suspects_detected += 1

            self.current_suspect = suspect
            self.last_known_position = suspect.get_position()
            self.alert_level = 100
            self.set_state("pursuing")

        else:
            self.current_suspect = None

        return suspects

    def report_incident(self, row, col):
        self.incident_location = (row, col)
        self.alert_level = max(self.alert_level, 60)

        if self.alive:
            self.set_state("investigating")

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
        if not self.alive or self.energy <= 0:
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

    def patrol(self, environment):
        if not self.alive:
            return False

        self.set_state("patrolling")

        if not self.patrol_points:
            return self.wander(environment)

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
            self.patrol_steps += 1

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

        row, col = self.random.choice(neighbors)

        moved = self.move(
            row - self.row,
            col - self.col,
            environment
        )

        if moved:
            self.patrol_steps += 1

        return moved

    def investigate(self, environment):
        if self.incident_location is None:
            return False

        self.set_state("investigating")

        if self.get_position() == self.incident_location:
            self.incident_location = None
            self.incidents_resolved += 1
            self.alert_level = 0
            return True

        moved = self.move_towards(
            self.incident_location,
            environment
        )

        if moved:
            self.investigations += 1

        return moved

    def pursue_suspect(self, environment):
        suspect = self.current_suspect

        if suspect is None or not suspect.alive:
            return False

        self.set_state("pursuing")

        self.last_known_position = suspect.get_position()

        if self.distance_to(suspect) <= self.attack_range:
            return self.attack_suspect()

        return self.move_towards(
            suspect.get_position(),
            environment
        )

    def attack_suspect(self):
        suspect = self.current_suspect

        if suspect is None or not suspect.alive:
            return False

        if self.distance_to(suspect) > self.attack_range:
            return False

        self.set_state("attacking")

        if self.attack(suspect):
            self.attacks_made += 1
            return True

        return False

    def search_last_position(self, environment):
        if self.last_known_position is None:
            return False

        if self.get_position() == self.last_known_position:
            self.last_known_position = None
            self.alert_level = 0
            return False

        self.set_state("searching")

        return self.move_towards(
            self.last_known_position,
            environment
        )

    def decide_action(self, agents, environment):
        if not self.alive:
            return "dead"

        self.detect_suspects(agents)

        if self.current_suspect is not None:
            self.pursue_suspect(environment)
            return self.state

        if self.incident_location is not None:
            self.investigate(environment)
            return self.state

        if self.last_known_position is not None:
            if self.search_last_position(environment):
                return self.state

        self.patrol(environment)

        return self.state

    def get_status(self):
        status = super().get_status()

        status.update({
            "officer_id": self.officer_id,
            "alert_level": self.alert_level,
            "current_suspect": (
                self.current_suspect.name
                if self.current_suspect is not None
                else None
            ),
            "incident_location": self.incident_location,
            "last_known_position": self.last_known_position,
            "patrol_steps": self.patrol_steps,
            "investigations": self.investigations,
            "suspects_detected": self.suspects_detected,
            "attacks_made": self.attacks_made,
            "incidents_resolved": self.incidents_resolved
        })

        return status
