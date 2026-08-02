import json

def analyze_v5_match():
    with open('Report/match-b48a8fc6-8d7c-4d10-93c0-39ff917be9fd.json', 'r') as f:
        data = json.load(f)

    steps = data.get("steps", [])
    info = data.get("info", {})

    print(f"=== DEEP V5 MATCH STEP-BY-STEP DIAGNOSTIC ===")
    print(f"Winner: P{info.get('winner')} | Scores: {info.get('scores')}")

    p0_launches = 0
    p1_launches = 0
    p0_ships_sent = 0
    p1_ships_sent = 0

    p0_first_launch_step = None
    p1_first_launch_step = None

    for s_idx, s in enumerate(steps):
        acts = s.get("action", s.get("actions", []))
        p0_act = acts[0] if len(acts) > 0 else []
        p1_act = acts[1] if len(acts) > 1 else []

        if p0_act:
            if p0_first_launch_step is None:
                p0_first_launch_step = s_idx
            p0_launches += len(p0_act)
            p0_ships_sent += sum(l[2] for l in p0_act if len(l) >= 3)

        if p1_act:
            if p1_first_launch_step is None:
                p1_first_launch_step = s_idx
            p1_launches += len(p1_act)
            p1_ships_sent += sum(l[2] for l in p1_act if len(l) >= 3)

    print(f"Player 0: First Launch Step = {p0_first_launch_step} | Total Launches = {p0_launches} | Total Ships Sent = {p0_ships_sent}")
    print(f"Player 1: First Launch Step = {p1_first_launch_step} | Total Launches = {p1_launches} | Total Ships Sent = {p1_ships_sent}")

    # Track planet ownership over time
    print("\n--- Planet Count Progression ---")
    for s_idx in range(0, len(steps), 50):
        obs = steps[s_idx].get("observation", {})
        planets = obs.get("planets", [])
        p0_count = sum(1 for p in planets if p[1] == 0)
        p1_count = sum(1 for p in planets if p[1] == 1)
        neutral_count = sum(1 for p in planets if p[1] == -1)
        print(f"Step {s_idx:3d}: P0 Planets = {p0_count:2d} | P1 Planets = {p1_count:2d} | Neutrals = {neutral_count:2d}")

if __name__ == '__main__':
    analyze_v5_match()
