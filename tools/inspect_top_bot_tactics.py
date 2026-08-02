import json

def inspect_top_bot():
    with open('Report/replay_68fea411-f65e-4f4b-b56d-ef847a9059d7.json', 'r') as f:
        data = json.load(f)

    info = data.get("info", {})
    winner = info.get("winner")
    steps = data.get("steps", [])

    print(f"=== REPLAY 68FEA411 INSPECTION ===")
    print(f"Winner: P{winner} | Final Scores: {info.get('scores')}")

    # Find steps with maximum launches by winner
    launch_steps = []
    for s_idx, s in enumerate(steps):
        acts = s.get("action", [])
        w_act = acts[winner] if len(acts) > winner else []
        if len(w_act) >= 5:
            launch_steps.append((s_idx, len(w_act), w_act))

    print(f"\nSteps with >= 5 simultaneous launches by winner: {len(launch_steps)}")
    for s_idx, count, act in launch_steps[:5]:
        print(f"\n--- Step {s_idx}: {count} Parallel Fleet Launches ---")
        for launch in act[:6]:
            print(f"   From Planet {launch[0]}: Angle {launch[1]:.3f} rad ({math.degrees(launch[1]):.1f}°), Ships: {launch[2]}")

if __name__ == '__main__':
    import math
    inspect_top_bot()
