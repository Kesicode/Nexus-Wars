import json
import os
import glob

def analyze_replay(filepath):
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except Exception as e:
        return None

    info = data.get("info", {})
    steps = data.get("steps", [])
    if not steps:
        return None

    winner = info.get("winner")
    scores = info.get("scores", [0, 0])
    reason = info.get("reason", "unknown")

    p0_launches = 0
    p1_launches = 0
    p0_ships = 0
    p1_ships = 0
    p0_step0_launch = False
    p1_step0_launch = False

    p0_parallel_max = 0
    p1_parallel_max = 0

    for s_idx, s in enumerate(steps):
        acts = s.get("action", s.get("actions", []))
        p0_act = acts[0] if len(acts) > 0 else []
        p1_act = acts[1] if len(acts) > 1 else []

        if p0_act:
            if s_idx == 0: p0_step0_launch = True
            p0_launches += len(p0_act)
            p0_ships += sum(l[2] for l in p0_act if len(l) >= 3)
            p0_parallel_max = max(p0_parallel_max, len(p0_act))

        if p1_act:
            if s_idx == 0: p1_step0_launch = True
            p1_launches += len(p1_act)
            p1_ships += sum(l[2] for l in p1_act if len(l) >= 3)
            p1_parallel_max = max(p1_parallel_max, len(p1_act))

    return {
        "file": os.path.basename(filepath),
        "winner": winner,
        "scores": scores,
        "reason": reason,
        "p0_launches": p0_launches,
        "p1_launches": p1_launches,
        "p0_ships": p0_ships,
        "p1_ships": p1_ships,
        "p0_step0": p0_step0_launch,
        "p1_step0": p1_step0_launch,
        "p0_parallel": p0_parallel_max,
        "p1_parallel": p1_parallel_max
    }

def main():
    files = glob.glob("Report/*.json")
    print(f"==================================================")
    print(f" ANALYZING ALL {len(files)} REPLAY REPORTS IN Report/")
    print(f"==================================================")

    p0_wins = 0
    p1_wins = 0
    draws = 0

    for f in files:
        res = analyze_replay(f)
        if not res: continue

        w = res["winner"]
        if w == 0: p0_wins += 1
        elif w == 1: p1_wins += 1
        else: draws += 1

        print(f"[{res['file'][:30]}] Winner: P{w} | Scores: P0={res['scores'][0]} P1={res['scores'][1]} | P0 Launch: {res['p0_launches']} (MaxParallel={res['p0_parallel']}, S0={res['p0_step0']}) | P1 Launch: {res['p1_launches']} (MaxParallel={res['p1_parallel']}, S0={res['p1_step0']})")

    print(f"\nSummary: P0 Wins = {p0_wins} | P1 Wins = {p1_wins} | Draws = {draws}")

if __name__ == '__main__':
    main()
