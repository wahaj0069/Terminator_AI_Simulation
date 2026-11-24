
from agents.base_agent import BaseAgent
from config import (
    T800_HEALTH,
    T800_SPEED,
    T800_VISION,
    T800_DAMAGE,
    MAX_ENERGY
)


class T800(BaseAgent):
    def __init__(self, row, col):
        super().__init__(
            name="T-800",
            agent_type="t800",
            row=row,
            col=col,
            health=T800_HEALTH,
            energy=MAX_ENERGY,
            speed=T800_SPEED,
            vision=T800_VISION,
            damage=T800_DAMAGE
        )

        self.state = "guarding"
        self.protectee = None
        self.current_threat = None

        self.enemies_detected = 0
        self.attacks_made = 0
        self.successful_interceptions = 0

        self.guard_distance = 3
        self.attack_range = 1

    def assign_protectee(self, agent):
        self.protectee = agent

        if agent is not None:
            agent.set_protector(self)

        self.set_state("guarding")

    def detect_enemies(self, agents):
        enemies = []

        for agent in agents:
            if not agent.alive:
                continue

            if agent.agent_type != "t1000":
                continue

            if self.can_see(agent):
                enemies.append(agent)

        if enemies:
            self.current_threat = min(
                enemies,
                key=lambda enemy: self.distance_to(enemy)
            )

            self.enemies_detected += len(enemies)

        else:
            self.current_threat = None

        return enemies

    def assess_threat(self, enemy):
        if enemy is None or not enemy.alive:
            return 0

        distance_to_self = self.distance_to(enemy)

        if self.protectee is not None:
            distance_to_john = self.protectee.distance_to(
                enemy
            )
        else:
            distance_to_john = float("inf")

        score = 0

        if distance_to_john <= 2:
            score += 70

        elif distance_to_john <= 5:
            score += 45

        elif distance_to_john <= 8:
            score += 20

        if distance_to_self <= self.attack_range:
            score += 30

        elif distance_to_self <= 4:
            score += 15

        return min(score, 100)

    def choose_move_towards(self, target, environment):
        neighbors = environment.get_neighbors(
            self.row,
            self.col
        )

        if not neighbors:
            return None

        current_distance = self.distance_to(target)

        best_position = min(
            neighbors,
            key=lambda position: (
                (position[0] - target.row) ** 2
                + (position[1] - target.col) ** 2
            )
        )

        new_distance = (
            (best_position[0] - target.row) ** 2
            + (best_position[1] - target.col) ** 2
        ) ** 0.5

        if new_distance >= current_distance:
            return None

        return best_position

    def move_towards(self, target, environment):
        if target is None or not target.alive:
            return False

        position = self.choose_move_towards(
            target,
            environment
        )

        if position is None:
            return False

        row, col = position

        return self.move(
            row - self.row,
            col - self.col,
            environment
        )

    def guard_john(self, environment):
        if self.protectee is None:
            return False

        if not self.protectee.alive:
            self.set_state("idle")
            return False

        distance = self.distance_to(
            self.protectee
        )

        if distance <= self.guard_distance:
            self.set_state("guarding")
            return True

        self.set_state("following")

        return self.move_towards(
            self.protectee,
            environment
        )

    def intercept_enemy(self, environment):
        enemy = self.current_threat

        if enemy is None or not enemy.alive:
            return False

        if self.protectee is None:
            return False

        threat_level = self.assess_threat(enemy)

        if threat_level < 20:
            return False

        self.set_state("intercepting")

        if self.distance_to(enemy) <= self.attack_range:
            return self.engage_enemy()

        moved = self.move_towards(
            enemy,
            environment
        )

        if moved:
            self.successful_interceptions += 1

        return moved

    def engage_enemy(self):
        enemy = self.current_threat

        if enemy is None or not enemy.alive:
            return False

        if self.distance_to(enemy) > self.attack_range:
            return False

        self.set_state("attacking")

        if self.attack(enemy):
            self.attacks_made += 1
            return True

        return False

    def decide_action(self, agents, environment):
        if not self.alive:
            return "dead"

        self.detect_enemies(agents)

        if self.current_threat is not None:
            threat_level = self.assess_threat(
                self.current_threat
            )

            if threat_level >= 20:
                self.intercept_enemy(environment)
                return self.state

        if self.protectee is not None:
            self.guard_john(environment)
            return self.state

        self.set_state("idle")
        return self.state

    def get_status(self):
        status = super().get_status()

        status.update({
            "protectee": (
                self.protectee.name
                if self.protectee is not None
                else None
            ),
            "current_threat": (
                self.current_threat.name
                if self.current_threat is not None
                else None
            ),
            "enemies_detected": self.enemies_detected,
            "attacks_made": self.attacks_made,
            "successful_interceptions": (
                self.successful_interceptions
            ),
            "guard_distance": self.guard_distance
        })

        return status
