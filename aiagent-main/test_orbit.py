import json
import math
import os

CENTER = 50.0
ROTATION_RADIUS_LIMIT = 50.0

def get_planet_position_at_step(init_p, step, angular_velocity):
    dx = init_p[2] - CENTER
    dy = init_p[3] - CENTER
    r = math.sqrt(dx*dx + dy*dy)
    if r + init_p[4] >= ROTATION_RADIUS_LIMIT:
        return init_p[2], init_p[3]
    initial_angle = math.atan2(dy, dx)
    current_angle = initial_angle + angular_velocity * step
    return CENTER + r * math.cos(current_angle), CENTER + r * math.sin(current_angle)

def main():
    replay_path = 'c:/Users/USER/OneDrive/Desktop/aibot/replay.json'
    with open(replay_path, 'r') as f:
        replay = json.load(f)

    steps = replay['steps']
    # Look at planet 12 at step 15 actual
    obs_15 = steps[15]['observation']
    angular_vel = obs_15.get('angular_velocity', 0.035)
    init_planets = obs_15['initial_planets']
    init_p12 = next(p for p in init_planets if p[0] == 12)
    actual_p12 = next(p for p in obs_15['planets'] if p[0] == 12)

    print(f"Initial p12: {init_p12}")
    print(f"Actual p12 at step 15: {actual_p12[2]:.4f}, {actual_p12[3]:.4f}")

    for step_val in [13, 14, 15, 16]:
        x, y = get_planet_position_at_step(init_p12, step_val, angular_vel)
        print(f"get_planet_pos(step={step_val}): {x:.4f}, {y:.4f}")

if __name__ == '__main__':
    main()
