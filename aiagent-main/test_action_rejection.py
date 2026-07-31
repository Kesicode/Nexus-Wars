import json

def main():
    with open('c:/Users/USER/OneDrive/Desktop/aibot/replay.json', 'r') as f:
        replay = json.load(f)

    step_30 = replay['steps'][30]
    obs = step_30['observation']
    action = step_30['action']

    p19_obs = next(p for p in obs['planets'] if p[0] == 19)
    print(f"Planet 19 at step 30 start: owner={p19_obs[1]}, ships={p19_obs[5]}, energy={p19_obs[7]}")
    print(f"Actions at step 30: Player 0: {action[0]}, Player 1: {action[1]}")
    print(f"Fleets at step 30: {obs.get('fleets', [])}")

    step_31 = replay['steps'][31]
    obs_31 = step_31['observation']
    p19_obs_31 = next(p for p in obs_31['planets'] if p[0] == 19)
    print(f"Planet 19 at step 31 start: owner={p19_obs_31[1]}, ships={p19_obs_31[5]}, energy={p19_obs_31[7]}")
    print(f"Fleets at step 31: {obs_31.get('fleets', [])}")

    # Let's also check if there is any other info or log
    print(f"Reward: {step_30['reward']}, Status: {step_30['status']}")

if __name__ == '__main__':
    main()
