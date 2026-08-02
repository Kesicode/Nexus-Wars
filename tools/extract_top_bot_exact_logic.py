import json

def analyze_top_bot_actions():
    with open('Report/replay_68fea411-f65e-4f4b-b56d-ef847a9059d7.json', 'r') as f:
        data = json.load(f)

    steps = data.get("steps", [])
    info = data.get("info", {})
    winner = info.get("winner")

    print(f"=== DEEP ANALYSIS OF TOP WINNING BOT (P{winner}) IN MATCH 68fea411 ===")

    win_launches = []
    launch_sizes = []
    launch_intervals = []
    last_launch_step = {}

    for s_idx, s in enumerate(steps[:100]): # Inspect first 100 steps
        acts = s.get("action", s.get("actions", []))
        if len(acts) > winner:
            win_act = acts[winner]
            if win_act:
                print(f"\nStep {s_idx:3d}: P{winner} executed {len(win_act)} launches:")
                for l in win_act:
                    src = l[0]
                    angle = l[1]
                    ships = l[2]
                    launch_sizes.append(ships)
                    print(f"   -> Src Planet {src:2d}: Angle={angle:+.3f} rad ({math.degrees(angle):+6.1f} deg), Ships={ships}")

import math
if __name__ == '__main__':
    analyze_top_bot_actions()
