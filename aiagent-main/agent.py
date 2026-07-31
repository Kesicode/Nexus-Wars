import json
import math
import sys
import os

# --------------------------------------------------------------------------
# Constants (matching the game engine specs)
# --------------------------------------------------------------------------
BOARD_SIZE = 100.0
CENTER = 50.0
SUN_RADIUS = 10.0
ROTATION_RADIUS_LIMIT = 50.0
LAUNCH_COST = 20

# --------------------------------------------------------------------------
# Geometry Helpers
# --------------------------------------------------------------------------
def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def point_to_segment_distance(p, v, w):
    """Minimum distance from point p to line segment v-w."""
    l2 = (v[0] - w[0]) ** 2 + (v[1] - w[1]) ** 2
    if l2 == 0.0:
        return distance(p, v)
    t = max(0, min(1, ((p[0] - v[0]) * (w[0] - v[0]) + (p[1] - v[1]) * (w[1] - v[1])) / l2))
    projection = (v[0] + t * (w[0] - v[0]), v[1] + t * (w[1] - v[1]))
    return distance(p, projection)

def swept_pair_hit(A, B, P0, P1, r):
    """True iff fleet segment A->B and planet segment P0->P1 come within r."""
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
    """Calculate fleet speed based on ship count."""
    if ships <= 0:
        return 0
    return min(6.0, 1.0 + 5.0 * (math.log(max(ships, 1)) / math.log(1000)) ** 1.5)

def get_planet_position_at_step(init_p, step, angular_velocity):
    """Compute planet position at given step (accounts for orbital motion)."""
    dx = init_p[2] - CENTER
    dy = init_p[3] - CENTER
    r = math.sqrt(dx*dx + dy*dy)
    if r + init_p[4] >= ROTATION_RADIUS_LIMIT:
        return init_p[2], init_p[3]
    initial_angle = math.atan2(dy, dx)
    current_angle = initial_angle + angular_velocity * step
    return CENTER + r * math.cos(current_angle), CENTER + r * math.sin(current_angle)

# --------------------------------------------------------------------------
# Simulation Representation
# --------------------------------------------------------------------------
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

    def copy(self):
        return PlanetSimState([self.id, self.owner, self.x, self.y, self.radius, self.ships, self.production, self.energy, self.energy_cap, self.energy_regen])

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

    def copy(self):
        return FleetSimState([self.id, self.owner, self.x, self.y, self.angle, self.from_planet_id, self.ships, self.launched_step])

def simulate_forward(planets, fleets, current_step, steps_to_simulate, planet_positions_cache):
    """
    Simulates the board forward up to steps_to_simulate steps using cached positions.
    """
    sim_planets = {p[0]: PlanetSimState(p) for p in planets}
    sim_fleets = [FleetSimState(f) for f in fleets]

    history = []
    history.append({pid: p.copy() for pid, p in sim_planets.items()})

    for s in range(current_step + 1, current_step + steps_to_simulate + 1):
        # 1. Production + energy regen for owned planets
        for pid, p in sim_planets.items():
            if p.owner != -1:
                p.ships += p.production
                p.energy = min(p.energy_cap, p.energy + p.energy_regen)

        # 2. Planet movement paths (from cache)
        planet_paths = {}
        for pid, p in sim_planets.items():
            p_old = (p.x, p.y)
            p_new = planet_positions_cache[s][pid]
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
                dx = f_old[0] - p.x
                dy = f_old[1] - p.y
                limit = 8.5 + p.radius
                if dx*dx + dy*dy > limit*limit:
                    continue

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

        history.append({pid: p.copy() for pid, p in sim_planets.items()})

    return history

# --------------------------------------------------------------------------
# Nexus Wars Expert Agent
# --------------------------------------------------------------------------
class NexusAgent:
    def __init__(self):
        self.enemy_fleet_count_history = []
        self.enemy_aggression = 0.5
        self.enemy_preferred_targets = {}
        self.home_planet_id = None
        self.enemy_depleted_planets = {}

    def update_enemy_modeling(self, step, me, fleets):
        enemy_id = 1 - me
        enemy_fleets = [f for f in fleets if f[1] == enemy_id]
        
        # Age out depleted enemy planets tracking
        self.enemy_depleted_planets = {pid: exp for pid, exp in self.enemy_depleted_planets.items() if exp > step}
        
        new_launches = 0
        for ef in enemy_fleets:
            if step - ef[7] <= 1:
                new_launches += 1
                from_id = ef[5]
                self.enemy_preferred_targets[from_id] = self.enemy_preferred_targets.get(from_id, 0) + 1
                # Mark source planet as depleted for counterattacks
                self.enemy_depleted_planets[from_id] = step + 15

        self.enemy_fleet_count_history.append(new_launches)
        recent_window = self.enemy_fleet_count_history[-20:]
        if recent_window:
            avg_launches = sum(recent_window) / len(recent_window)
            self.enemy_aggression = min(1.0, avg_launches * 2.0)

    def get_game_phase(self, step, my_planets, enemy_planets, planets):
        total_planets = len(planets)
        my_count = len(my_planets)
        enemy_count = len(enemy_planets)
        neutral_count = total_planets - my_count - enemy_count
        
        my_ships = sum(p[5] for p in my_planets)
        enemy_ships = sum(p[5] for p in enemy_planets)
        
        my_prod = sum(p[6] for p in my_planets)
        enemy_prod = sum(p[6] for p in enemy_planets)

        if enemy_ships < 40 or enemy_count <= 1:
            return "killer_instinct"
        # Fix 4: Stronger recovery trigger — also activate on planet-count gap
        if my_count < enemy_count - 1 or (my_ships < enemy_ships * 0.55 and step > 40) or (my_count < enemy_count * 0.5 and step > 30):
            return "recovery"
        if step < 100 and neutral_count > total_planets * 0.15:
            return "expansion"
        if my_ships > enemy_ships * 1.3 or my_prod > enemy_prod * 1.4 or my_count > total_planets * 0.55:
            return "domination"
        return "mid_game"

    def act(self, obs):
        me = obs["player"]
        step = obs["step"]
        angular_vel = obs.get("angular_velocity", 0.035)
        planets = obs["planets"]
        fleets = obs.get("fleets", [])
        initial_planets = obs.get("initial_planets", [])

        self.update_enemy_modeling(step, me, fleets)

        my_planets = [p for p in planets if p[1] == me]
        enemy_planets = [p for p in planets if p[1] == 1 - me]
        neutral_planets = [p for p in planets if p[1] == -1]

        if not my_planets:
            return []

        # Identify home planet
        if self.home_planet_id is None and my_planets:
            self.home_planet_id = my_planets[0][0]

        phase = self.get_game_phase(step, my_planets, enemy_planets, planets)

        # Cache planet positions up to 80 steps forward
        sim_steps = min(80, 500 - step - 1)
        if sim_steps <= 0:
            return []

        init_planets_dict = {p[0]: p for p in initial_planets}
        planet_positions_cache = {}
        for s in range(step, step + sim_steps + 1):
            planet_positions_cache[s] = {}
            for p in planets:
                pid = p[0]
                planet_positions_cache[s][pid] = get_planet_position_at_step(init_planets_dict[pid], s, angular_vel)

        # Forward simulation with cached positions
        sim_history = simulate_forward(planets, fleets, step, sim_steps, planet_positions_cache)

        temp_energy = {p[0]: p[7] for p in my_planets}
        temp_ships = {p[0]: p[5] for p in my_planets}
        
        targeted_planet_ids = set()

        # Danger & min_keep limits
        min_keep = {}
        for mp in my_planets:
            pid = mp[0]
            threat_deficit = 0
            threat_tick = -1
            
            for t in range(1, sim_steps + 1):
                p_future = sim_history[t][pid]
                if p_future.owner != me:
                    threat_deficit = p_future.ships
                    threat_tick = t
                    break
            
            if threat_tick != -1:
                min_keep[pid] = max(4, int(threat_deficit * 0.8) + 2)
            else:
                if phase == "killer_instinct":
                    min_keep[pid] = 0
                else:
                    # Preemptive Frontline Danger Garrison
                    danger_val = 0
                    for ep in enemy_planets:
                        dist = distance((mp[2], mp[3]), (ep[2], ep[3]))
                        if dist < 35.0:
                            weight = (35.0 - dist) / 35.0
                            danger_val += max(0, ep[5] - 2) * weight
                    
                    cap = 40 if mp[6] >= 3 else 25
                    min_keep[pid] = min(cap, max(2, 2 + int(danger_val * 0.15)))
            
            # Extra safety anchor for home planet
            # Fix 1: In first 15 steps, keep only 3 ships so we can always make first expansion
            if pid == self.home_planet_id and phase != "killer_instinct":
                if step < 15:
                    min_keep[pid] = max(min_keep[pid], 3)
                else:
                    min_keep[pid] = max(min_keep[pid], 6)

        actions = []

        def path_crosses_sun(src_pos, dst_pos):
            return point_to_segment_distance((CENTER, CENTER), src_pos, dst_pos) < SUN_RADIUS

        # ----------------------------------------------------------------------
        # Layer 1: Defense Strategy (Reinforce threatened own planets)
        # ----------------------------------------------------------------------
        threatened_planets = []
        for mp in my_planets:
            pid = mp[0]
            for t in range(1, sim_steps + 1):
                p_future = sim_history[t][pid]
                if p_future.owner != me:
                    threatened_planets.append((pid, t, p_future.ships))
                    break

        threatened_planets.sort(key=lambda x: x[1])

        for target_id, t_loss, deficit in threatened_planets:
            arrival_step = step + t_loss
            target_pos = planet_positions_cache[arrival_step][target_id]
            target_init = init_planets_dict[target_id]
            
            needed = deficit + 3
            
            # Find all possible reserves
            reserves = []
            for src in my_planets:
                src_id = src[0]
                if src_id == target_id:
                    continue
                src_pos = (src[2], src[3])
                dist = distance(src_pos, target_pos)
                eff_dist = max(1.0, dist - src[4] - target_init[4] - 0.1) # exact offset
                
                avail_ships = temp_ships[src_id] - min_keep.get(src_id, 2)
                if avail_ships <= 0 or temp_energy[src_id] < LAUNCH_COST:
                    continue
                
                max_spd = fleet_speed(avail_ships)
                min_travel = eff_dist / max_spd
                
                # Allow arriving up to 2 steps late to immediately recapture
                if min_travel <= t_loss + 2:
                    if min_travel <= t_loss:
                        v_req = eff_dist / t_loss
                        if v_req < 1.0:
                            n_req = 10
                        elif v_req <= 6.0:
                            n_req = math.ceil(1000 ** (((v_req - 1.0) / 5.0) ** (2/3)))
                        else:
                            n_req = -1
                    else:
                        n_req = avail_ships
                        
                    if 0 < n_req <= avail_ships:
                        reserves.append((src_id, n_req, dist, src_pos))

            # Fight or Flight verification
            total_possible = sum(r[1] for r in reserves)
            if total_possible < needed and target_id != self.home_planet_id:
                # Flight: let the planet go to conserve ships for counterattacks
                continue

            reserves.sort(key=lambda x: x[2])
            help_sent = 0

            for src_id, n_req, dist, src_pos in reserves:
                if help_sent >= needed:
                    break
                if path_crosses_sun(src_pos, target_pos):
                    continue
                if temp_energy[src_id] < LAUNCH_COST:
                    continue

                send = min(temp_ships[src_id] - min_keep.get(src_id, 2), max(n_req, needed - help_sent))
                if send >= 5:
                    angle = math.atan2(target_pos[1] - src_pos[1], target_pos[0] - src_pos[0])
                    actions.append([src_id, angle, send])
                    
                    temp_ships[src_id] -= send
                    temp_energy[src_id] -= LAUNCH_COST
                    help_sent += send
                    targeted_planet_ids.add(target_id)

        # ----------------------------------------------------------------------
        # Layer 2: Tactical Counter-Snipes
        # ----------------------------------------------------------------------
        # Land exactly 1 tick after an enemy captures a neutral to take it with minimum force.
        for nt in neutral_planets:
            tid = nt[0]
            if tid in targeted_planet_ids:
                continue
            
            t_init = init_planets_dict[tid]
            
            t_cap = -1
            for t in range(1, sim_steps + 1):
                p_future = sim_history[t][tid]
                if p_future.owner == 1 - me:
                    t_cap = t
                    break
            
            if t_cap != -1:
                future_garrison = sim_history[t_cap][tid].ships
                needed = future_garrison + 2
                
                arr_step = t_cap + 1
                if arr_step > sim_steps:
                    continue
                target_pos = planet_positions_cache[step + arr_step][tid]
                
                for src in my_planets:
                    src_id = src[0]
                    src_pos = (src[2], src[3])
                    avail = temp_ships[src_id] - min_keep.get(src_id, 2)
                    
                    if avail < needed or temp_energy[src_id] < LAUNCH_COST:
                        continue
                    
                    dist_val = distance(src_pos, target_pos)
                    eff_dist = max(1.0, dist_val - src[4] - nt[4] - 0.1) # exact offset
                    v_req = eff_dist / arr_step
                    
                    if 1.0 <= v_req <= 6.0:
                        n_req = math.ceil(1000 ** (((v_req - 1.0) / 5.0) ** (2/3)))
                        send = max(8, n_req)
                        if send <= avail and not path_crosses_sun(src_pos, target_pos):
                            angle = math.atan2(target_pos[1] - src_pos[1], target_pos[0] - src_pos[0])
                            actions.append([src_id, angle, send])
                            
                            temp_ships[src_id] -= send
                            temp_energy[src_id] -= LAUNCH_COST
                            targeted_planet_ids.add(tid)
                            break

        # ----------------------------------------------------------------------
        # Layer 3: Single-Planet Neutral Expansion
        # ----------------------------------------------------------------------
        if phase == "expansion" or phase == "mid_game" or phase == "killer_instinct":
            for src in my_planets:
                src_id = src[0]
                src_pos = (src[2], src[3])
                avail = temp_ships[src_id] - min_keep.get(src_id, 2)
                
                # Fix 1: Lower min_launch in first 15 steps to ensure first expansion is never blocked
                if phase == "killer_instinct":
                    min_launch = 8
                elif step < 15:
                    min_launch = 8  # allow smaller opening fleets
                else:
                    min_launch = 12
                if avail < min_launch or temp_energy[src_id] < LAUNCH_COST:
                    continue

                valid_neutrals = []
                for nt in neutral_planets:
                    tid = nt[0]
                    if tid in targeted_planet_ids:
                        continue
                    
                    t_prod = nt[6]
                    if t_prod <= 2 and phase == "expansion" and temp_energy[src_id] < 60:
                        continue

                    t_init = init_planets_dict[tid]
                    future_garrison_0 = nt[5]
                    
                    n_send = max(min_launch, future_garrison_0 + 2)
                    if avail < n_send:
                        if t_prod >= 4 and avail >= 15:
                            n_send = avail
                        else:
                            continue
                            
                    speed = fleet_speed(n_send)
                    
                    arr_t = -1
                    for t_candidate in range(1, 60):
                        t_pos = planet_positions_cache[step + t_candidate][tid]
                        dist_val = distance(src_pos, t_pos)
                        eff_dist = max(1.0, dist_val - src[4] - nt[4] - 0.1) # exact offset
                        if t_candidate >= eff_dist / speed:
                            arr_t = t_candidate
                            target_pos = t_pos
                            break
                    
                    if arr_t != -1 and not path_crosses_sun(src_pos, target_pos):
                        future_garrison = sim_history[arr_t][tid].ships
                        future_owner = sim_history[arr_t][tid].owner
                        if future_owner == me:
                            continue
                        
                        # Enemy proximity penalty: do not expand into the enemy's teeth
                        enemy_penalty = 0
                        if enemy_planets:
                            min_enemy_dist = min((distance((ep[2], ep[3]), target_pos) for ep in enemy_planets))
                            if min_enemy_dist < 25.0 and distance(src_pos, target_pos) > min_enemy_dist * 1.5:
                                enemy_penalty = (25.0 - min_enemy_dist) * 2.0

                        # Close-range captures: use tighter buffer to strike faster
                        capture_buffer = 1 if arr_t <= 8 else 2
                        needed = max(min_launch, future_garrison + capture_buffer)
                        if avail >= needed:
                            score = t_prod * 50
                            
                            if step < 30:
                                score -= distance(src_pos, target_pos) * 1.5
                            else:
                                score -= distance(src_pos, target_pos) * 0.4
                                
                            if t_prod <= 2:
                                score -= 60
                            # Reinforcement potential bonus
                            our_close_planets = sum(1 for p in my_planets if distance((p[2], p[3]), (target_pos[0], target_pos[1])) < 30.0)
                            score += our_close_planets * 10
                            # Fix 2: Production-leverage bonus — reward upgrades above our current avg prod
                            my_avg_prod = sum(p[6] for p in my_planets) / len(my_planets)
                            if t_prod > my_avg_prod:
                                score += (t_prod - my_avg_prod) * 30
                            score -= enemy_penalty
                            valid_neutrals.append((score, tid, needed, target_pos))
                        elif t_prod >= 2 and avail >= 12 and needed - avail <= 18:
                            score = t_prod * 40 - distance(src_pos, target_pos) * 0.4 - future_garrison * 0.2 - enemy_penalty
                            valid_neutrals.append((score, tid, avail, target_pos))

                if valid_neutrals:
                    valid_neutrals.sort(key=lambda x: -x[0])
                    _, best_tid, send_ships, target_pos = valid_neutrals[0]
                    angle = math.atan2(target_pos[1] - src_pos[1], target_pos[0] - src_pos[0])
                    actions.append([src_id, angle, send_ships])
                    
                    temp_ships[src_id] -= send_ships
                    temp_energy[src_id] -= LAUNCH_COST
                    targeted_planet_ids.add(best_tid)

        # ----------------------------------------------------------------------
        # Layer 4: Coordinated Attacks (Enemy & Neutrals)
        # ----------------------------------------------------------------------
        potential_targets = [p for p in planets if p[1] != me]
        scored_targets = []
        for t in potential_targets:
            tid = t[0]
            if tid in targeted_planet_ids:
                continue
            t_owner = t[1]
            t_prod = t[6]
            
            base_score = t_prod * 50
            if t_prod <= 2:
                base_score -= 60
            
            if t_owner == -1:
                base_score += 30 - t[5] * 0.5
            else:
                base_score += 15 - t[5] * 0.2
                if phase == "domination":
                    base_score += 40

            min_dist = min((distance((p[2], p[3]), (t[2], t[3])) for p in my_planets), default=999)
            base_score -= min_dist * 0.4
            
            # Counterattack bonus on depleted enemy planets if close enough to exploit
            if tid in self.enemy_depleted_planets and min_dist < 40.0:
                base_score += 50
            
            # Proximity check to enemy (danger/reinforcement potential discount)
            if enemy_planets:
                min_enemy_dist = min((distance((ep[2], ep[3]), (t[2], t[3])) for ep in enemy_planets))
                if min_enemy_dist < 25.0 and min_dist > min_enemy_dist * 1.5:
                    base_score -= (25.0 - min_enemy_dist) * 2.0
            
            # Reinforcement potential bonus
            our_close_planets = sum(1 for p in my_planets if distance((p[2], p[3]), (t[2], t[3])) < 30.0)
            base_score += our_close_planets * 10
            
            # Fix 2: Production-leverage bonus in coordinated scoring too
            if my_planets:
                my_avg_prod = sum(p[6] for p in my_planets) / len(my_planets)
                if t_prod > my_avg_prod:
                    base_score += (t_prod - my_avg_prod) * 30
            
            scored_targets.append((base_score, t))

        scored_targets.sort(key=lambda x: -x[0])

        for _, target in scored_targets[:6]:
            tid = target[0]
            if tid in targeted_planet_ids:
                continue
            t_init = init_planets_dict[tid]
            
            best_arrival_t = -1
            best_launch_plan = []
            max_synchronized_ships = 0
            
            for t_arr in range(1, 60):
                arrival_step = step + t_arr
                target_pos = planet_positions_cache[arrival_step][tid]
                
                launch_plan = []
                total_ships_possible = 0
                
                for src in my_planets:
                    src_id = src[0]
                    src_pos = (src[2], src[3])
                    
                    if temp_energy[src_id] < LAUNCH_COST:
                        continue
                        
                    dist_to_t = distance(src_pos, target_pos)
                    eff_dist = max(1.0, dist_to_t - src[4] - t_init[4] - 0.1) # exact offset
                    v_req = eff_dist / t_arr
                    
                    if 1.0 <= v_req <= 6.0:
                        n_req = math.ceil(1000 ** (((v_req - 1.0) / 5.0) ** (2/3)))
                        avail = temp_ships[src_id] - min_keep.get(src_id, 2)
                        
                        # Fix 1: lower coord launch threshold in first 15 steps
                        if phase == "killer_instinct":
                            min_coord_launch = 8
                        elif step < 15:
                            min_coord_launch = 8
                        else:
                            min_coord_launch = 12
                        if min_coord_launch <= n_req <= avail:
                            if not path_crosses_sun(src_pos, target_pos):
                                launch_plan.append((src_id, n_req, src_pos, target_pos))
                                total_ships_possible += n_req

                if total_ships_possible > max_synchronized_ships:
                    max_synchronized_ships = total_ships_possible
                    best_launch_plan = launch_plan
                    best_arrival_t = t_arr

            if best_launch_plan and best_arrival_t != -1:
                future_state = sim_history[best_arrival_t][tid]
                garrison = future_state.ships
                
                buffer = 2 if target[1] == -1 else 8
                if phase == "domination":
                    buffer = 15
                
                # Dynamic enemy reinforcement buffer check
                enemy_reinforce_pot = 0
                if target[1] != -1:
                    target_pos = planet_positions_cache[step + best_arrival_t][tid]
                    for ep in enemy_planets:
                        if ep[0] == tid:
                            continue
                        d_ep_t = distance((ep[2], ep[3]), target_pos)
                        eff_d_ep_t = max(1.0, d_ep_t - ep[4] - t_init[4] - 0.1)
                        min_t_ep_t = eff_d_ep_t / 6.0
                        if min_t_ep_t <= best_arrival_t:
                            enemy_reinforce_pot += max(0, ep[5] - 5)

                needed = max(15, garrison + buffer + int(enemy_reinforce_pot * 0.4))
                
                if max_synchronized_ships >= needed:
                    current_sum = 0
                    for src_id, n_req, src_pos, target_pos in sorted(best_launch_plan, key=lambda x: -x[1]):
                        if current_sum >= needed:
                            break
                        if temp_energy[src_id] < LAUNCH_COST:
                            continue
                        
                        angle = math.atan2(target_pos[1] - src_pos[1], target_pos[0] - src_pos[0])
                        actions.append([src_id, angle, n_req])
                        
                        temp_ships[src_id] -= n_req
                        temp_energy[src_id] -= LAUNCH_COST
                        current_sum += n_req
                        targeted_planet_ids.add(tid)
                elif target[6] >= 4 and max_synchronized_ships >= 18:
                    current_sum = 0
                    for src_id, n_req, src_pos, target_pos in sorted(best_launch_plan, key=lambda x: -x[1]):
                        if temp_energy[src_id] < LAUNCH_COST:
                            continue
                        angle = math.atan2(target_pos[1] - src_pos[1], target_pos[0] - src_pos[0])
                        actions.append([src_id, angle, n_req])
                        temp_ships[src_id] -= n_req
                        temp_energy[src_id] -= LAUNCH_COST
                        current_sum += n_req
                        targeted_planet_ids.add(tid)

        # ----------------------------------------------------------------------
        # Layer 5: Planet-Count Emergency Spread Mode (Fix 3)
        # ----------------------------------------------------------------------
        # If enemy has >= 2.5x our planet count AND we have planets sitting on 80+ ships,
        # force-attack the closest weakest enemy planet to break out of hoarding.
        if enemy_planets and len(enemy_planets) >= len(my_planets) * 2.5 and len(my_planets) > 0:
            # Find our richest planet
            rich_src = max(my_planets, key=lambda p: temp_ships[p[0]])
            rich_id = rich_src[0]
            rich_avail = temp_ships[rich_id] - min_keep.get(rich_id, 2)
            if rich_avail >= 30 and temp_energy[rich_id] >= LAUNCH_COST:
                # Find weakest (fewest ships) enemy planet closest to us
                src_pos = (rich_src[2], rich_src[3])
                best_spread_target = None
                best_spread_score = float('-inf')
                for ep in enemy_planets:
                    tid = ep[0]
                    if tid in targeted_planet_ids:
                        continue
                    d = distance(src_pos, (ep[2], ep[3]))
                    # Score: low garrison + low distance = best spread target
                    spread_score = -ep[5] - d * 0.5
                    if spread_score > best_spread_score and not path_crosses_sun(src_pos, (ep[2], ep[3])):
                        best_spread_score = spread_score
                        best_spread_target = ep
                if best_spread_target:
                    t_pos = (best_spread_target[2], best_spread_target[3])
                    angle = math.atan2(t_pos[1] - src_pos[1], t_pos[0] - src_pos[0])
                    # Send half our available ships — enough to threaten, not everything
                    send = max(20, min(rich_avail, rich_avail * 2 // 3))
                    actions.append([rich_id, angle, send])
                    temp_ships[rich_id] -= send
                    temp_energy[rich_id] -= LAUNCH_COST
                    targeted_planet_ids.add(best_spread_target[0])

        # ----------------------------------------------------------------------
        # Layer 6: Energy Banking & Opportunistic Snipe
        # ----------------------------------------------------------------------
        if step >= 50:
            for src in my_planets:
                src_id = src[0]
                e_cap = src[8]
                e_val = temp_energy[src_id]
                
                # We need a true surplus of ships to justify spending energy
                min_avail = 25 if e_val >= e_cap - 5 else 35
                trigger_energy = e_cap - 20
                
                if e_val >= trigger_energy:
                    avail = temp_ships[src_id] - min_keep.get(src_id, 2)
                    if avail >= min_avail:
                        best_target = None
                        best_dist = float("inf")
                        for t in enemy_planets: # ONLY enemy owned planets
                            tid = t[0]
                            if tid in targeted_planet_ids:
                                continue
                            t_pos = planet_positions_cache[step + 20][tid]
                            d = distance((src[2], src[3]), t_pos)
                            # Only target relatively close planets to make snipes effective
                            if d < 45.0 and d < best_dist and not path_crosses_sun((src[2], src[3]), t_pos):
                                best_dist = d
                                best_target = (tid, t_pos)
                                
                        if best_target:
                            tid, t_pos = best_target
                            angle = math.atan2(t_pos[1] - src[3], t_pos[0] - src[2])
                            send = min(avail, max(12, avail // 2))
                            if send >= min_avail:
                                actions.append([src_id, angle, send])
                                temp_ships[src_id] -= send
                                temp_energy[src_id] -= LAUNCH_COST
                                targeted_planet_ids.add(tid)

        return actions

def main():
    agent = NexusAgent()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            obs = json.loads(line)
        except json.JSONDecodeError:
            continue
            
        actions = agent.act(obs)
        sys.stdout.write(json.dumps(actions) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
