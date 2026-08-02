import json
import glob
import os
import math

def analyze_opponent_replays():
    files = glob.glob("Report/*.json")
    print(f"=== DEEP ANALYSIS OF {len(files)} NEW TOP OPPONENT LADDER REPLAYS ===")

    results = []

    for fpath in files:
        with open(fpath, 'r') as f:
            data = json.load(f)

        info = data.get("info", {})
        winner = info.get("winner", -1)
        steps = data.get("steps", [])

        if winner == -1 and steps and "reward" in steps[-1]:
            r = steps[-1]["reward"]
            if r[0] > r[1]:
                winner = 0
            elif r[1] > r[0]:
                winner = 1

        w_id = winner
        l_id = 1 - winner if winner in (0, 1) else -1

        # Track winner launch tactics
        w_launches_per_step = []
        w_fleet_sizes = []
        w_target_types = {"neutral": 0, "enemy": 0, "own": 0}
        
        step0_act = steps[0].get("action", [])
        w_step0 = step0_act[w_id] if w_id != -1 and len(step0_act) > w_id else []
        l_step0 = step0_act[l_id] if l_id != -1 and len(step0_act) > l_id else []

        for s_idx, s in enumerate(steps):
            acts = s.get("action", s.get("actions", []))
            if w_id != -1 and len(acts) > w_id and acts[w_id]:
                w_launches_per_step.append(len(acts[w_id]))
                for l in acts[w_id]:
                    if len(l) >= 3:
                        w_fleet_sizes.append(l[2])

        results.append({
            "file": os.path.basename(fpath),
            "winner": winner,
            "reason": info.get("reason", "unknown"),
            "scores": info.get("scores", [0, 0]),
            "steps": len(steps),
            "w_step0": w_step0,
            "l_step0": l_step0,
            "w_total_launches": len(w_fleet_sizes),
            "w_avg_fleet": sum(w_fleet_sizes) / len(w_fleet_sizes) if w_fleet_sizes else 0,
            "w_max_launches_in_step": max(w_launches_per_step) if w_launches_per_step else 0
        })

    p0_wins = sum(1 for r in results if r['winner'] == 0)
    p1_wins = sum(1 for r in results if r['winner'] == 1)

    print(f"P0 Wins: {p0_wins} ({p0_wins/len(results)*100:.1f}%) | P1 Wins: {p1_wins} ({p1_wins/len(results)*100:.1f}%)")
    
    step0_winner_launches = sum(1 for r in results if r['w_step0'])
    print(f"Winning bots executing Step-0 launch: {step0_winner_launches}/{len(results)} ({step0_winner_launches/len(results)*100:.1f}%)")
    
    avg_fleet_all = sum(r['w_avg_fleet'] for r in results) / len(results) if results else 0
    print(f"Winner average launch fleet size: {avg_fleet_all:.1f} ships")
    
    max_multi_launch = max(r['w_max_launches_in_step'] for r in results) if results else 0
    print(f"Max parallel launches in single step by winner: {max_multi_launch} fleets simultaneously")

    print("\n--- Top Replay Samples ---")
    for r in results[:10]:
        print(f"File: {r['file'][:30]:30s} | Winner: P{r['winner']} | Steps: {r['steps']:3d} | W_Step0: {str(r['w_step0']):25s} | W_AvgFleet: {r['w_avg_fleet']:4.1f} | MaxParallel: {r['w_max_launches_in_step']}")

if __name__ == '__main__':
    analyze_opponent_replays()
