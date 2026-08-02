import json

def main():
    replay_path = 'c:/Users/USER/OneDrive/Desktop/aibot/replay.json'
    with open(replay_path, 'r') as f:
        replay = json.load(f)

    steps = replay['steps']
    
    track_steps = [0, 50, 100, 150, 200, 250, 300, 310, 320, 325, 328, 329]
    for ts in track_steps:
        if ts >= len(steps):
            break
        obs = steps[ts]['observation']
        my_planets = [p for p in obs['planets'] if p[1] == 0]
        enemy_planets = [p for p in obs['planets'] if p[1] == 1]
        my_fleets = [f for f in obs.get('fleets', []) if f[1] == 0]
        enemy_fleets = [f for f in obs.get('fleets', []) if f[1] == 1]
        
        my_ships = sum(p[5] for p in my_planets) + sum(f[6] for f in my_fleets)
        enemy_ships = sum(p[5] for p in enemy_planets) + sum(f[6] for f in enemy_fleets)
        
        print(f"Step {ts}:")
        print(f"  Agent (Player 0): Planets={len(my_planets)}, Ships={my_ships}")
        print(f"  Enemy (Player 1): Planets={len(enemy_planets)}, Ships={enemy_ships}")
        if len(my_planets) > 0 and len(my_planets) <= 3:
            print(f"  Agent Planet details: {[(p[0], p[5], p[6]) for p in my_planets]}")

if __name__ == '__main__':
    main()
