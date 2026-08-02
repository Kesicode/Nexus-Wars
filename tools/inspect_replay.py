import json
import os

def main():
    replay_path = 'c:/Users/USER/OneDrive/Desktop/aibot/replay.json'
    if not os.path.exists(replay_path):
        print("replay.json not found!")
        return

    with open(replay_path, 'r') as f:
        replay = json.load(f)

    print("Winner:", replay['info']['winner'])
    print("Reason:", replay['info']['reason'])
    print("Scores:", replay['info']['scores'])
    print("Total Steps:", len(replay['steps']))

    # Print first few steps
    for step_idx in range(min(15, len(replay['steps']))):
        step_data = replay['steps'][step_idx]
        print(f"Step {step_idx}:")
        print(f"  Actions: Player 0 (Agent): {step_data['action'][0]}, Player 1 (Starter): {step_data['action'][1]}")
        print(f"  Status: {step_data['status']}")
        
    # Check if there was any error or death
    dead_steps = [idx for idx, s in enumerate(replay['steps']) if s['status'][0] != 'ACTIVE']
    if dead_steps:
        print(f"Agent was not ACTIVE at steps: {dead_steps[:10]}")
    else:
        print("Agent remained ACTIVE throughout the match.")

    # Print final planet ownership
    final_obs = replay['steps'][-1]['observation']
    my_planets = [p for p in final_obs['planets'] if p[1] == 0]
    enemy_planets = [p for p in final_obs['planets'] if p[1] == 1]
    neutral_planets = [p for p in final_obs['planets'] if p[1] == -1]
    print(f"Final Planet Counts: Agent: {len(my_planets)}, Starter: {len(enemy_planets)}, Neutral: {len(neutral_planets)}")
    print(f"Final Planet Details (ID, Owner, Ships, Prod):")
    for p in sorted(final_obs['planets'], key=lambda x: x[0]):
        print(f"  Planet {p[0]}: Owner={p[1]}, Ships={p[5]}, Prod={p[6]}")

if __name__ == '__main__':
    main()
