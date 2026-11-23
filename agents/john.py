
from agents.base_agent import BaseAgent
from config import (
    JOHN_HEALTH,
    JOHN_SPEED,
    JOHN_VISION,
    MAX_ENERGY
)


class JohnConnor(BaseAgent):
    def __init__(self, row, col):
        super().__init__(
            name="John Connor",
            agent_type="john",
            row=row,
            col=col,
            health=JOHN_HEALTH,
            energy=MAX_ENERGY,
            speed=JOHN_SPEED,
            vision=JOHN_VISION,
            damage=0
        )

        self.state = "exploring"
        self.safe_zone_reached = False
        self.threat_detected = False
        self.nearest_threat = None
        self.protector = None

        self.escape_count = 0
        self.time_survived = 0
        self.danger_level = 0

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
            self.nearest_threat = min(
                threats,
                key=lambda agent: self.distance_to(agent)
            )

            self.threat_detected = True
            self.danger_level = self.calculate_danger(
                self.nearest_threat
            )

            self.set_state("fleeing")

        else:
            self.nearest_threat = None
            self.threat_detected = False
            self.danger_level = 0

        return threats

    def calculate_danger(self, threat):
        distance = self.distance_to(threat)

        if distance <= 1:
            return 100

        if distance <= 3:
            return 80

        if distance <= 5:
            return 50

        if distance <= self.vision:
            return 25

        return 0

    def choose_escape_position(self, environment):
        if self.nearest_threat is None:
            return None

        neighbors = environment.get_neighbors(
            self.row,
            self.col
        )

        if not neighbors:
            return None

        best_position = max(
            neighbors,
            key=lambda position: (
                (position[0] - self.nearest_threat.row) ** 2
                + (position[1] - self.nearest_threat.col) ** 2
            )
        )

        return best_position

    def flee(self, environment):
        if not self.alive:
            return False

        if self.nearest_threat is None:
            return False

        position = self.choose_escape_position(
            environment
        )

        if position is None:
            return False

        new_row, new_col = position

        dr = new_row - self.row
        dc = new_col - self.col

        if self.move(dr, dc, environment):
            self.escape_count += 1
            self.set_state("fleeing")
            return True

        return False

    def check_safe_zone(self, environment):
        tile = environment.get_tile(
            self.row,
            self.col
        )

        if tile == "safe_zone":
            self.safe_zone_reached = True
            self.set_state("safe")
            return True

        self.safe_zone_reached = False
        return False

    def set_protector(self, agent):
        self.protector = agent

    def update_survival_time(self, delta_time):
        if self.alive:
            self.time_survived += max(
                0,
                delta_time
            )

    def decide_state(self):
        if not self.alive:
            return "dead"

        if self.safe_zone_reached:
            self.set_state("safe")

        elif self.threat_detected:
            self.set_state("fleeing")

        elif self.protector is not None and self.protector.alive:
            self.set_state("protected")

        else:
            self.set_state("exploring")

        return self.state

    def get_status(self):
        status = super().get_status()

        status.update({
            "safe_zone_reached": self.safe_zone_reached,
            "threat_detected": self.threat_detected,
            "danger_level": self.danger_level,
            "escape_count": self.escape_count,
            "time_survived": round(
                self.time_survived, 2
            ),
            "protector": (
                self.protector.name
                if self.protector is not None
                else None
            )
        })

        return status
