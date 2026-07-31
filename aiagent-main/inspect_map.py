import json

def main():
    replay_path = 'c:/Users/USER/OneDrive/Desktop/aibot/replay.json'
    with open(replay_path, 'r') as f:
        replay = json.load(f)

    obs = replay['steps'][0]['observation']
    print("Sun is at (50.0, 50.0)")
    print("Initial Planets:")
    for p in sorted(obs['planets'], key=lambda x: x[0]):
        print(f"  Planet {p[0]}: Owner={p[1]}, x={p[2]:.2f}, y={p[3]:.2f}, Radius={p[4]:.2f}, Ships={p[5]}, Prod={p[6]}")

if __name__ == '__main__':
    main()
