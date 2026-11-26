
from agents.base_agent import BaseAgent
from config import (
    SARAH_HEALTH,
    SARAH_SPEED,
    SARAH_VISION,
    MAX_ENERGY
)


class SarahConnor(BaseAgent):
    def __init__(self, row, col):
        super().__init__(
            name="Sarah Connor",
            agent_type="sarah",
            row=row,
            col=col,
            health=SARAH_HEALTH,
            energy=MAX_ENERGY,
            speed=SARAH_SPEED,
            vision=SARAH_VISION,
            damage=8
        )

        self.state = "searching"
        self.john = None
        self.current_threat = None
        self.last_known_john_position = None

        self.support_distance = 3
        self.attack_range = 1

        self.threats_detected = 0
        self.attacks_made = 0
        self.support_actions = 0
        self.escape_assists = 0

    def assign_john(self, john):
        self.john = john

        if john is not None:
            self.last_known_john_position = john.get_position()

        self.set_state("supporting")

    def detect_threats(self, agents):
        threats = []

        for agent in agents:
            if not agent.alive:
                continue

            if agent.agent_type != "t1000":
                continue

            if self.can_see(agent):
                threats.append(agent)

        if threats:
            self.current_threat = min(
                threats,
                key=lambda agent: self.distance_to(agent)
            )

            self.threats_detected += len(threats)

        else:
            self.current_threat = None

        return threats

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

    def follow_john(self, environment):
        if self.john is None or not self.john.alive:
            return False

        self.last_known_john_position = self.john.get_position()

        distance = self.distance_to(self.john)

        if distance <= self.support_distance:
            self.set_state("supporting")
            return True

        self.set_state("following")

        moved = self.move_towards(
            self.john.get_position(),
            environment
        )

        if moved:
            self.support_actions += 1

        return moved

    def protect_john(self, environment):
        if self.john is None or not self.john.alive:
            return False

        if self.current_threat is None:
            return self.follow_john(environment)

        threat = self.current_threat

        john_distance = self.john.distance_to(threat)

        if john_distance > 5:
            return self.follow_john(environment)

        if self.distance_to(threat) <= self.attack_range:
            self.set_state("defending")

            if self.attack(threat):
                self.attacks_made += 1
                self.escape_assists += 1
                return True

        self.set_state("intercepting")

        moved = self.move_towards(
            threat.get_position(),
            environment
        )

        if moved:
            self.support_actions += 1

        return moved

    def seek_john(self, environment):
        if self.john is not None and self.john.alive:
            return self.follow_john(environment)

        if self.last_known_john_position is None:
            return False

        self.set_state("searching")

        return self.move_towards(
            self.last_known_john_position,
            environment
        )

    def decide_action(self, agents, environment):
        if not self.alive:
            return "dead"

        self.detect_threats(agents)

        if self.john is not None and self.john.alive:
            if self.current_threat is not None:
                self.protect_john(environment)
            else:
                self.follow_john(environment)

            return self.state

        if self.last_known_john_position is not None:
            self.seek_john(environment)
            return self.state

        self.set_state("idle")
        return self.state

    def get_status(self):
        status = super().get_status()

        status.update({
            "john": (
                self.john.name
                if self.john is not None
                else None
            ),
            "current_threat": (
                self.current_threat.name
                if self.current_threat is not None
                else None
            ),
            "last_known_john_position": (
                self.last_known_john_position
            ),
            "threats_detected": self.threats_detected,
            "attacks_made": self.attacks_made,
            "support_actions": self.support_actions,
            "escape_assists": self.escape_assists
        })

        return status
