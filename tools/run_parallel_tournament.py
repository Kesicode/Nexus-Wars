import subprocess
import json
import os
import time
from multiprocessing import Pool, cpu_count

def run_match(args):
    p0, p1, seed = args
    cmd = [
        'python', 'reference/main.py',
        '--agents', f"python {p0}", f"python {p1}",
        '--seed', str(seed)
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
        out = res.stdout.strip()
        if "winner=" in out:
            parts = out.split()
            winner_str = [p for p in parts if p.startswith("winner=")][0].split("=")[1]
            return (p0, p1, seed, int(winner_str) if winner_str != "None" else -1)
    except Exception:
        return (p0, p1, seed, -2)
    return (p0, p1, seed, -2)

def main():
    opponents = [
        'tournament_bots/simple_bot.py',
        'tournament_bots/viper.py',
        'tournament_bots/fortress.py'
    ]
    my_agent = 'agent.py'
    seeds = [100 + i * 13 for i in range(20)]  # 20 seeds x 3 bots x 2 roles = 120 matches!

    tasks = []
    for opp in opponents:
        for s in seeds:
            tasks.append((my_agent, opp, s))
            tasks.append((opp, my_agent, s))

    num_cores = cpu_count()
    print(f"==========================================================")
    print(f" PARALLEL TOURNAMENT RUNNER ({len(tasks)} MATCHES ON {num_cores} CORES)")
    print(f"==========================================================")

    start_time = time.time()
    with Pool(processes=num_cores) as pool:
        results = pool.map(run_match, tasks)
    elapsed = time.time() - start_time

    wins = 0
    losses = 0
    draws = 0

    for p0, p1, s, winner in results:
        if p0 == my_agent:
            if winner == 0: wins += 1
            elif winner == 1: losses += 1
            else: draws += 1
        else:
            if winner == 1: wins += 1
            elif winner == 0: losses += 1
            else: draws += 1

    total = len(tasks)
    win_rate = (wins / total) * 100

    print(f"\nCompleted in {elapsed:.2f} seconds ({total / elapsed:.1f} matches/sec)")
    print(f"Total Matches: {total}")
    print(f"Wins:   {wins} ({win_rate:.1f}%)")
    print(f"Losses: {losses}")
    print(f"Draws:  {draws}")
    print(f"==========================================================")

if __name__ == '__main__':
    main()
