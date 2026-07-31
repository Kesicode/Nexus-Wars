import json
import math
import sys
import os

CENTER = 50.0
SUN_RADIUS = 10.0
ROTATION_RADIUS_LIMIT = 50.0
BOARD_SIZE = 100.0
LAUNCH_COST = 20

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def point_to_segment_distance(p, v, w):
    l2 = (v[0] - w[0]) ** 2 + (v[1] - w[1]) ** 2
    if l2 == 0.0:
        return distance(p, v)
    t = max(0, min(1, ((p[0] - v[0]) * (w[0] - v[0]) + (p[1] - v[1]) * (w[1] - v[1])) / l2))
    projection = (v[0] + t * (w[0] - v[0]), v[1] + t * (w[1] - v[1]))
    return distance(p, projection)

def swept_pair_hit(A, B, P0, P1, r):
    d0x, d0y = A[0] - P0[0], A[1] - P0[1]
    dvx = (B[0] - A[0]) - (P1[0] - P0[0])
    dvy = (B[1] - A[1]) - (P1[1] - P0[1])
    a = dvx * dvx + dvy * dvy
    b = 2.0 * (d0x * dvx + d0y * dvy)
    c = d0x * d0x + d0y * d0y - r * r
    if a < 1e-12:
        return c <= 0.0
    disc = b * b - 4.0 * a * c
    if disc < 0.0:
        return False
    sq = math.sqrt(disc)
    t1 = (-b - sq) / (2.0 * a)
    t2 = (-b + sq) / (2.0 * a)
    return t2 >= 0.0 and t1 <= 1.0

def fleet_speed(ships):
    if ships <= 0:
        return 0
    return min(6.0, 1.0 + 5.0 * (math.log(max(ships, 1)) / math.log(1000)) ** 1.5)

def get_planet_position_at_step(init_p, step, angular_velocity):
    dx = init_p[2] - CENTER
    dy = init_p[3] - CENTER
    r = math.sqrt(dx*dx + dy*dy)
    if r + init_p[4] >= ROTATION_RADIUS_LIMIT:
        return init_p[2], init_p[3]
    initial_angle = math.atan2(dy, dx)
    current_angle = initial_angle + angular_velocity * step
    return CENTER + r * math.cos(current_angle), CENTER + r * math.sin(current_angle)

class PlanetSimState:
    def __init__(self, p_list):
        self.id = p_list[0]
        self.owner = p_list[1]
        self.x = p_list[2]
        self.y = p_list[3]
        self.radius = p_list[4]
        self.ships = p_list[5]
        self.production = p_list[6]
        self.energy = p_list[7]
        self.energy_cap = p_list[8]
        self.energy_regen = p_list[9]

class FleetSimState:
    def __init__(self, f_list):
        self.id = f_list[0]
        self.owner = f_list[1]
        self.x = f_list[2]
        self.y = f_list[3]
        self.angle = f_list[4]
        self.from_planet_id = f_list[5]
        self.ships = f_list[6]
        self.launched_step = f_list[7]

def simulate_forward(planets, fleets, initial_planets, angular_velocity, current_step, steps_to_simulate, next_fleet_id, steps_actions=None):
    sim_planets = {p[0]: PlanetSimState(p) for p in planets}
    sim_fleets = [FleetSimState(f) for f in fleets]
    init_planets_dict = {p[0]: p for p in initial_planets}

    for s in range(current_step + 1, current_step + steps_to_simulate + 1):
        # 0. Apply actions for step s (since we are simulating the tick starting at step s)
        engine_step = s
        if steps_actions and engine_step in steps_actions:
            actions_list = steps_actions[engine_step]
            for player_id, action in enumerate(actions_list):
                if not action or not isinstance(action, list):
                    continue
                for move in action:
                    if len(move) != 3:
                        continue
                    from_id, angle, ships = move
                    ships = int(ships)
                    from_planet = sim_planets.get(from_id)
                    if from_planet and from_planet.owner == player_id:
                        if ships <= 0 or from_planet.ships < ships or from_planet.energy < LAUNCH_COST:
                            print(f"  [SIM] Skipping launch: step={engine_step}, planet={from_id}, owner={player_id}, ships_launch={ships}, planet_ships={from_planet.ships}, energy={from_planet.energy}")
                            continue
                        print(f"  [SIM] Launching: step={engine_step}, planet={from_id}, owner={player_id}, ships={ships}, energy_before={from_planet.energy}")
                        from_planet.ships -= ships
                        from_planet.energy -= LAUNCH_COST
                        start_x = from_planet.x + math.cos(angle) * (from_planet.radius + 0.1)
                        start_y = from_planet.y + math.sin(angle) * (from_planet.radius + 0.1)
                        sim_fleets.append(FleetSimState([next_fleet_id, player_id, start_x, start_y, angle, from_id, ships, engine_step]))
                        next_fleet_id += 1

        # 1. Production + energy regen
        for pid, p in sim_planets.items():
            if p.owner != -1:
                p.ships += p.production
                p.energy = min(p.energy_cap, p.energy + p.energy_regen)

        # 2. Planet movement paths
        planet_paths = {}
        for pid, p in sim_planets.items():
            p_old = (p.x, p.y)
            p_new = get_planet_position_at_step(init_planets_dict[pid], s, angular_velocity)
            planet_paths[pid] = (p_old, p_new)

        # 3. Fleet movement and collision detection
        fleets_to_remove = set()
        combat_lists = {pid: [] for pid in sim_planets}

        for fleet in sim_fleets:
            angle = fleet.angle
            ships = fleet.ships
            speed = fleet_speed(ships)
            f_old = (fleet.x, fleet.y)
            fleet.x += math.cos(angle) * speed
            fleet.y += math.sin(angle) * speed
            f_new = (fleet.x, fleet.y)

            # Check planet collisions
            hit_planet = False
            for pid, p in sim_planets.items():
                p_old, p_new = planet_paths[pid]
                if swept_pair_hit(f_old, f_new, p_old, p_new, p.radius):
                    combat_lists[pid].append(fleet)
                    fleets_to_remove.add(fleet)
                    hit_planet = True
                    break

            if hit_planet:
                continue

            # Out of bounds
            if not (0 <= fleet.x <= BOARD_SIZE and 0 <= fleet.y <= BOARD_SIZE):
                fleets_to_remove.add(fleet)
                continue

            # Sun collision
            if point_to_segment_distance((CENTER, CENTER), f_old, f_new) < SUN_RADIUS:
                fleets_to_remove.add(fleet)
                continue

        # 4. Apply planet position updates
        for pid, p in sim_planets.items():
            p_old, p_new = planet_paths[pid]
            p.x, p.y = p_new

        # Remove dead fleets
        sim_fleets = [f for f in sim_fleets if f not in fleets_to_remove]

        # 5. Combat resolution
        for pid, arriving in combat_lists.items():
            if not arriving:
                continue
            p = sim_planets[pid]
            player_ships = {}
            for fleet in arriving:
                player_ships[fleet.owner] = player_ships.get(fleet.owner, 0) + fleet.ships

            sorted_players = sorted(player_ships.items(), key=lambda it: it[1], reverse=True)
            top_player, top_ships = sorted_players[0]

            if len(sorted_players) > 1:
                survivor_ships = top_ships - sorted_players[1][1]
                survivor_owner = top_player if survivor_ships > 0 else -1
            else:
                survivor_owner = top_player
                survivor_ships = top_ships

            if survivor_ships > 0:
                if p.owner == survivor_owner:
                    p.ships += survivor_ships
                else:
                    p.ships -= survivor_ships
                    if p.ships < 0:
                        p.owner = survivor_owner
                        p.ships = abs(p.ships)

    return sim_planets, sim_fleets

def run_tests():
    replay_path = 'c:/Users/USER/OneDrive/Desktop/aibot/replay.json'
    if not os.path.exists(replay_path):
        print("replay.json not found! Run a match first.")
        sys.exit(1)

    with open(replay_path, 'r') as f:
        replay = json.load(f)

    steps = replay['steps']
    num_steps = len(steps)
    print(f"Total steps in replay: {num_steps}")

    # Build action dictionary by step
    steps_actions = {}
    for idx, s_data in enumerate(steps):
        steps_actions[idx] = s_data['action']

    # We will test predicting steps forward from multiple start steps
    for start_step in range(0, min(200, num_steps - 30), 10):
        start_obs = steps[start_step]['observation']
        angular_vel = start_obs.get('angular_velocity', 0.035)
        initial_planets = start_obs['initial_planets']
        next_fleet_id = start_obs.get('next_fleet_id', 0)

        steps_forward = 15
        pred_planets, pred_fleets = simulate_forward(
            start_obs['planets'],
            start_obs.get('fleets', []),
            initial_planets,
            angular_vel,
            start_step,
            steps_forward,
            next_fleet_id,
            steps_actions
        )

        actual_obs = steps[start_step + steps_forward]['observation']
        actual_planets = {p[0]: p for p in actual_obs['planets']}

        mismatches = 0
        for pid, p in pred_planets.items():
            ap = actual_planets[pid]
            owner_match = p.owner == ap[1]
            ships_match = abs(p.ships - ap[5]) <= 0.0001
            x_match = abs(p.x - ap[2]) < 0.01
            y_match = abs(p.y - ap[3]) < 0.01

            if not (owner_match and ships_match and x_match and y_match):
                print(f"Mismatch at step {start_step + steps_forward} for planet {pid}:")
                print(f"  Pred: owner={p.owner}, ships={p.ships}, pos=({p.x:.2f}, {p.y:.2f})")
                print(f"  Actual: owner={ap[1]}, ships={ap[5]}, pos=({ap[2]:.2f}, {ap[3]:.2f})")
                mismatches += 1

        if mismatches == 0:
            print(f"Step {start_step} -> {start_step + steps_forward}: 100% Match (with actions)!")
        else:
            print(f"Step {start_step} -> {start_step + steps_forward}: Fail with {mismatches} mismatches!")
            sys.exit(1)

    print("All forward simulation checks with action execution passed successfully!")

if __name__ == '__main__':
    run_tests()
