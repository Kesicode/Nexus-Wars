import os
import json
import sys
import subprocess
import itertools

def run_match(bot_a_path, bot_b_path, seed):
    # Run match using main.py with specific agents and seed
    cmd = [
        'python', 'reference/main.py',
        '--agents', f"python {bot_a_path}", f"python {bot_b_path}",
        '--seed', str(seed),
        '--out', 'temp_replay.json'
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        # Parse output for winner
        # Output is like: seed=123 steps=500 winner=0 reason=steps scores=[...] durationMs=...
        output = result.stdout.strip()
        if "winner=" in output:
            parts = output.split()
            winner_part = [p for p in parts if p.startswith("winner=")][0]
            winner = winner_part.split("=")[1]
            if winner == "None":
                return -1  # Draw
            return int(winner)
    except Exception as e:
        print(f"Error running match: {e}")
        return -2  # Error/crash
    return -2

def main():
    bot_dir = 'tournament_bots'
    bots = [os.path.join(bot_dir, f) for f in os.listdir(bot_dir) if f.endswith('.py')]
    
    print("Found bots for tournament:")
    for b in bots:
        print(f"  - {os.path.basename(b)}")

    # 5 rounds per pair
    rounds = 5
    seeds = [100 + i * 23 for i in range(rounds)]

    # Standings stats
    # Bot name -> {wins, draws, losses, points}
    # Win = 3, Draw = 1, Loss = 0
    stats = {os.path.basename(b): {'wins': 0, 'draws': 0, 'losses': 0, 'points': 0} for b in bots}

    pairs = list(itertools.combinations(bots, 2))
    total_matches = len(pairs) * rounds
    match_count = 0

    print(f"\nStarting tournament: {len(bots)} bots, {len(pairs)} pairings, {rounds} rounds. Total {total_matches} matches.")

    for bot_a, bot_b in pairs:
        name_a = os.path.basename(bot_a)
        name_b = os.path.basename(bot_b)
        print(f"\nPairing: {name_a} vs {name_b}")

        for r in range(rounds):
            match_count += 1
            seed = seeds[r]
            
            # Alternate player seats
            if r % 2 == 0:
                winner_idx = run_match(bot_a, bot_b, seed)
                # winner_idx: 0 = bot_a, 1 = bot_b
                if winner_idx == 0:
                    stats[name_a]['wins'] += 1
                    stats[name_a]['points'] += 3
                    stats[name_b]['losses'] += 1
                    res = name_a
                elif winner_idx == 1:
                    stats[name_b]['wins'] += 1
                    stats[name_b]['points'] += 3
                    stats[name_a]['losses'] += 1
                    res = name_b
                elif winner_idx == -1:
                    stats[name_a]['draws'] += 1
                    stats[name_a]['points'] += 1
                    stats[name_b]['draws'] += 1
                    stats[name_b]['points'] += 1
                    res = "Draw"
                else:
                    res = "Error"
            else:
                winner_idx = run_match(bot_b, bot_a, seed)
                # winner_idx: 0 = bot_b, 1 = bot_a
                if winner_idx == 0:
                    stats[name_b]['wins'] += 1
                    stats[name_b]['points'] += 3
                    stats[name_a]['losses'] += 1
                    res = name_b
                elif winner_idx == 1:
                    stats[name_a]['wins'] += 1
                    stats[name_a]['points'] += 3
                    stats[name_b]['losses'] += 1
                    res = name_a
                elif winner_idx == -1:
                    stats[name_a]['draws'] += 1
                    stats[name_a]['points'] += 1
                    stats[name_b]['draws'] += 1
                    stats[name_b]['points'] += 1
                    res = "Draw"
                else:
                    res = "Error"
            
            print(f"  Match {r+1}/{rounds} (Seed {seed}): Winner = {res} ({match_count}/{total_matches})")

    # Sort standings by points
    standings = sorted(stats.items(), key=lambda x: -x[1]['points'])

    print("\n" + "="*50)
    print(" TOURNAMENT FINAL STANDINGS")
    print("="*50)
    print(f"{'Bot Name':<20} | {'Points':<6} | {'Wins':<5} | {'Draws':<5} | {'Losses':<6}")
    print("-"*50)
    for name, data in standings:
        print(f"{name:<20} | {data['points']:<6} | {data['wins']:<5} | {data['draws']:<5} | {data['losses']:<6}")
    print("="*50)

    # Clean up temp files
    try:
        if os.path.exists('temp_replay.json'):
            os.remove('temp_replay.json')
    except Exception:
        pass

if __name__ == '__main__':
    main()
