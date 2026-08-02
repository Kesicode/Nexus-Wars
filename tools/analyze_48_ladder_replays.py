import json
import glob
import os
import math

def analyze_replays():
    files = glob.glob("Report/*.json")
    print(f"=== DEEP ANALYSIS OF {len(files)} LADDER REPLAYS ===")

    p0_wins = 0
    p1_wins = 0
    p0_step0_launches = 0
    p1_step0_launches = 0

    p0_avg_fleet = []
    p1_avg_fleet = []

    for fpath in files:
        with open(fpath, 'r') as f:
            data = json.load(f)
        
        info = data.get("info", {})
        winner = info.get("winner", -1)
        steps = data.get("steps", [])

        if winner == 0:
            p0_wins += 1
        elif winner == 1:
            p1_wins += 1

        step0_act = steps[0].get("action", [])
        if len(step0_act) > 0 and step0_act[0]:
            p0_step0_launches += 1
        if len(step0_act) > 1 and step0_act[1]:
            p1_step0_launches += 1

        # Track fleet sizes
        for s in steps:
            acts = s.get("action", [])
            if len(acts) > 0 and acts[0]:
                for l in acts[0]:
                    if len(l) >= 3:
                        p0_avg_fleet.append(l[2])
            if len(acts) > 1 and acts[1]:
                for l in acts[1]:
                    if len(l) >= 3:
                        p1_avg_fleet.append(l[2])

    print(f"Total Replays: {len(files)}")
    print(f"P0 Wins: {p0_wins} ({p0_wins/len(files)*100:.1f}%) | P1 Wins: {p1_wins} ({p1_wins/len(files)*100:.1f}%)")
    print(f"P0 Step-0 Launch Rate: {p0_step0_launches}/{len(files)} ({p0_step0_launches/len(files)*100:.1f}%)")
    print(f"P1 Step-0 Launch Rate: {p1_step0_launches}/{len(files)} ({p1_step0_launches/len(files)*100:.1f}%)")
    print(f"P0 Avg Fleet Launch Size: {sum(p0_avg_fleet)/len(p0_avg_fleet):.1f} ships")
    print(f"P1 Avg Fleet Launch Size: {sum(p1_avg_fleet)/len(p1_avg_fleet):.1f} ships")

if __name__ == '__main__':
    analyze_replays()
