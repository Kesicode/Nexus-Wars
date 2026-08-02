import json
import glob
import os
import math

def parse_report(filepath):
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except Exception as e:
        return None

    info = data.get("info", {})
    winner = info.get("winner", None)
    if winner is None or winner == -1:
        # Check reward on last step
        steps = data.get("steps", [])
        if steps and "reward" in steps[-1]:
            r = steps[-1]["reward"]
            if r[0] > r[1]:
                winner = 0
            elif r[1] > r[0]:
                winner = 1
            else:
                return None

    steps = data.get("steps", [])
    if not steps:
        return None

    winner_id = winner
    loser_id = 1 - winner_id

    # Step 0 opening
    step0 = steps[0]
    actions = step0.get("action", step0.get("actions", []))
    winner_step0_actions = actions[winner_id] if len(actions) > winner_id else []

    winner_launches = []
    winner_launch_sizes = []

    for s_idx, step_data in enumerate(steps):
        acts = step_data.get("action", step_data.get("actions", []))
        w_act = acts[winner_id] if len(acts) > winner_id else []
        
        if w_act:
            for launch in w_act:
                if len(launch) >= 3:
                    src_id, angle, ships = launch[0], launch[1], launch[2]
                    winner_launch_sizes.append(ships)
                    winner_launches.append((s_idx, src_id, angle, ships))

    return {
        "file": os.path.basename(filepath),
        "winner": winner_id,
        "reason": info.get("reason", "unknown"),
        "scores": info.get("scores", [0, 0]),
        "total_steps": len(steps),
        "step0_launch": winner_step0_actions,
        "total_launches": len(winner_launches),
        "avg_launch_size": sum(winner_launch_sizes) / len(winner_launch_sizes) if winner_launch_sizes else 0,
        "max_launch_size": max(winner_launch_sizes) if winner_launch_sizes else 0,
        "min_launch_size": min(winner_launch_sizes) if winner_launch_sizes else 0,
    }

def main():
    report_files = glob.glob("Report/*.json")
    results = []
    
    for f in report_files:
        res = parse_report(f)
        if res:
            results.append(res)
            
    print(f"=== DEEP ANALYSIS OF ALL {len(results)} REPLAYS ===")
    
    p0_wins = sum(1 for r in results if r['winner'] == 0)
    p1_wins = sum(1 for r in results if r['winner'] == 1)
    print(f"P0 Wins: {p0_wins} | P1 Wins: {p1_wins}")
    
    step0_launch_count = sum(1 for r in results if r['step0_launch'])
    print(f"Winners executing Step-0 launch: {step0_launch_count} out of {len(results)} ({step0_launch_count/len(results)*100:.1f}%)")
    
    avg_launch_overall = sum(r['avg_launch_size'] for r in results) / len(results) if results else 0
    print(f"Winner average fleet launch size across all steps: {avg_launch_overall:.1f} ships")
    
    print("\n--- Detailed Breakout of 29 Replays ---")
    for r in results:
        print(f"File: {r['file'][:35]:35s} | Winner: P{r['winner']} | Steps: {r['total_steps']:3d} | Step0 Launch: {str(r['step0_launch']):25s} | Avg Fleet: {r['avg_launch_size']:4.1f} shp")

if __name__ == '__main__':
    main()
