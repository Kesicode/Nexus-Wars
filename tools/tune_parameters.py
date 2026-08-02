import subprocess
import json
import os
import itertools
from multiprocessing import Pool

def run_match_worker(args):
    p0_script, p1_script, seed = args
    cmd = [
        'python', 'reference/main.py',
        '--agents', f"python {p0_script}", f"python {p1_script}",
        '--seed', str(seed)
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        out = res.stdout.strip()
        if "winner=" in out:
            parts = out.split()
            winner_str = [p for p in parts if p.startswith("winner=")][0].split("=")[1]
            winner = None if winner_str == "None" else int(winner_str)
            return winner
    except Exception:
        return -2
    return -2

def main():
    opponents = [
        'tournament_bots/simple_bot.py',
        'tournament_bots/viper.py',
        'tournament_bots/fortress.py'
    ]
    my_agent = 'agent.py'
    seeds = [100 + i * 17 for i in range(10)]

    tasks = []
    for opp in opponents:
        for s in seeds:
            tasks.append((my_agent, opp, s))
            tasks.append((opp, my_agent, s))

    print(f"==================================================")
    print(f" FAST MULTI-PROCESS AGENT EVALUATOR ({len(tasks)} MATCHES)")
    print(f"==================================================")

    with Pool() as pool:
        results = pool.map(run_match_worker, tasks)

    wins = 0
    losses = 0
    draws = 0

    for idx, (p0, p1, s) in enumerate(tasks):
        w = results[idx]
        if p0 == my_agent:
            if w == 0: wins += 1
            elif w == 1: losses += 1
            else: draws += 1
        else:
            if w == 1: wins += 1
            elif w == 0: losses += 1
            else: draws += 1

    total = len(tasks)
    win_rate = (wins / total) * 100
    print(f"\nResults: Wins={wins}, Losses={losses}, Draws={draws}")
    print(f"Win Rate: {win_rate:.1f}%")

if __name__ == '__main__':
    main()
