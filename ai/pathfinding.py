
import heapq
import itertools
import math


class AStarPathfinder:
    def __init__(self, environment):
        self.environment = environment

        self.paths_calculated = 0
        self.successful_paths = 0
        self.failed_paths = 0
        self.total_nodes_explored = 0

    def heuristic(self, start, goal):
        return (
            abs(start[0] - goal[0])
            + abs(start[1] - goal[1])
        )

    def reconstruct_path(self, came_from, current):
        path = [current]

        while current in came_from:
            current = came_from[current]
            path.append(current)

        path.reverse()
        return path

    def find_path(self, start, goal):
        self.paths_calculated += 1

        start = tuple(start)
        goal = tuple(goal)

        if not self.environment.is_walkable(*start):
            self.failed_paths += 1
            return []

        if not self.environment.is_walkable(*goal):
            self.failed_paths += 1
            return []

        if start == goal:
            self.successful_paths += 1
            return []

        counter = itertools.count()

        open_heap = []
        heapq.heappush(
            open_heap,
            (self.heuristic(start, goal), next(counter), start)
        )

        came_from = {}
        g_score = {start: 0}
        closed_set = set()

        while open_heap:
            _, _, current = heapq.heappop(open_heap)

            if current in closed_set:
                continue

            self.total_nodes_explored += 1

            if current == goal:
                self.successful_paths += 1

                full_path = self.reconstruct_path(
                    came_from,
                    current
                )

                return full_path[1:]

            closed_set.add(current)

            neighbors = self.environment.get_neighbors(
                current[0],
                current[1]
            )

            for neighbor in neighbors:
                neighbor = tuple(neighbor)

                if neighbor in closed_set:
                    continue

                tentative_g = g_score[current] + 1

                if tentative_g < g_score.get(
                    neighbor,
                    math.inf
                ):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g

                    f_score = (
                        tentative_g
                        + self.heuristic(neighbor, goal)
                    )

                    heapq.heappush(
                        open_heap,
                        (f_score, next(counter), neighbor)
                    )

        self.failed_paths += 1
        return []

    def find_path_to_agent(self, agent, target):
        if not agent.alive or not target.alive:
            return []

        return self.find_path(
            agent.get_position(),
            target.get_position()
        )

    def find_path_to_location(self, agent, location_name):
        if not agent.alive:
            return []

        location = self.environment.get_location(
            location_name
        )

        if location is None:
            return []

        destination = location.get("position")

        if destination is None:
            return []

        return self.find_path(
            agent.get_position(),
            destination
        )

    def find_nearest_walkable(self, position):
        row, col = position

        if self.environment.is_walkable(row, col):
            return row, col

        grid = self.environment.grid

        best_position = None
        best_distance = math.inf

        for r in range(grid.rows):
            for c in range(grid.cols):
                if not self.environment.is_walkable(r, c):
                    continue

                distance = self.heuristic(
                    (row, col),
                    (r, c)
                )

                if distance < best_distance:
                    best_distance = distance
                    best_position = (r, c)

        return best_position

    def find_path_near_target(self, agent, target):
        if not agent.alive or not target.alive:
            return []

        target_position = target.get_position()

        candidates = [
            position
            for position in self.environment.get_neighbors(
                target_position[0],
                target_position[1]
            )
            if position != agent.get_position()
        ]

        candidates.sort(
            key=lambda position: self.heuristic(
                agent.get_position(),
                position
            )
        )

        best_path = None

        for position in candidates:
            path = self.find_path(
                agent.get_position(),
                position
            )

            if path and (
                best_path is None
                or len(path) < len(best_path)
            ):
                best_path = path

        return best_path if best_path is not None else []

    def calculate_path_cost(self, path):
        return len(path)

    def get_statistics(self):
        return {
            "paths_calculated": self.paths_calculated,
            "successful_paths": self.successful_paths,
            "failed_paths": self.failed_paths,
            "nodes_explored": self.total_nodes_explored
        }

    def reset_statistics(self):
        self.paths_calculated = 0
        self.successful_paths = 0
        self.failed_paths = 0
        self.total_nodes_explored = 0
