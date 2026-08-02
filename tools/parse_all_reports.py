import json
import glob
import os

def parse_report(filepath):
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except Exception as e:
        return None

    info = data.get("info", {})
    winner = info.get("winner", None)
    steps = data.get("steps", [])

    if winner is None or winner == -1:
        if steps and "reward" in steps[-1]:
            r = steps[-1]["reward"]
            if r[0] > r[1]:
                winner = 0
            elif r[1] > r[0]:
                winner = 1
            else:
                winner = -1

    scores = info.get("scores", [0, 0])
    reason = info.get("reason", "unknown")
    seed = data.get("seed", "unknown")
    players = data.get("players", [])

    # Check launches
    p0_launches = 0
    p1_launches = 0
    
    for s in steps:
        acts = s.get("action", s.get("actions", []))
        if len(acts) > 0 and acts[0]:
            p0_launches += len(acts[0])
        if len(acts) > 1 and acts[1]:
            p1_launches += len(acts[1])

    return {
        "file": os.path.basename(filepath),
        "seed": seed,
        "winner": winner,
        "reason": reason,
        "scores": scores,
        "total_steps": len(steps),
        "p0_launches": p0_launches,
        "p1_launches": p1_launches,
        "players": players
    }

def main():
    report_files = glob.glob("Report/*.json")
    results = []
    
    for f in report_files:
        res = parse_report(f)
        if res:
            results.append(res)
            
    print(f"==========================================================================")
    print(f" ANALYSIS OF ALL {len(results)} NEW LADDER MATCH REPLAYS IN Report/")
    print(f"==========================================================================")
    
    p0_wins = sum(1 for r in results if r['winner'] == 0)
    p1_wins = sum(1 for r in results if r['winner'] == 1)
    draws = sum(1 for r in results if r['winner'] == -1)

    print(f"Player 0 Wins: {p0_wins} ({p0_wins/len(results)*100:.1f}%)")
    print(f"Player 1 Wins: {p1_wins} ({p1_wins/len(results)*100:.1f}%)")
    print(f"Draws: {draws}")
    
    print("\n--- Match-by-Match Breakdown ---")
    for r in results:
        w_str = f"P{r['winner']}" if r['winner'] != -1 else "DRAW"
        sc_str = f"P0: {r['scores'][0]} vs P1: {r['scores'][1]}"
        print(f"File: {r['file'][:32]:32s} | Winner: {w_str:5s} | Reason: {r['reason']:12s} | Steps: {r['total_steps']:3d} | Scores: {sc_str}")

if __name__ == '__main__':
    main()
