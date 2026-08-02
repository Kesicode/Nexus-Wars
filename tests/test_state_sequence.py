import json

def main():
    with open('c:/Users/USER/OneDrive/Desktop/aibot/replay.json', 'r') as f:
        replay = json.load(f)

    for step_idx in range(27, 33):
        step_data = replay['steps'][step_idx]
        obs = step_data['observation']
        act = step_data['action']
        p19 = next(p for p in obs['planets'] if p[0] == 19)
        print(f"Step {step_idx}: obs.step={obs['step']}")
        print(f"  Planet 19: owner={p19[1]}, ships={p19[5]}, energy={p19[7]}")
        print(f"  Actions: Player 0: {act[0]}, Player 1: {act[1]}")
        print(f"  Fleets: {obs.get('fleets', [])}")

if __name__ == '__main__':
    main()
