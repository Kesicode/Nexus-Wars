import subprocess
import json
import os
import sys

def run_single_match(p0_script, p1_script, seed):
    cmd = [
        'python', 'reference/main.py',
        '--agents', f"python {p0_script}", f"python {p1_script}",
        '--seed', str(seed),
        '--out', 'replays/temp_evolution_replay.json'
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        out = res.stdout.strip()
        if "winner=" in out:
            parts = out.split()
            winner_str = [p for p in parts if p.startswith("winner=")][0].split("=")[1]
            steps_str = [p for p in parts if p.startswith("steps=")][0].split("=")[1]
            winner = None if winner_str == "None" else int(winner_str)
            steps = int(steps_str)
            return winner, steps
    except Exception as e:
        print(f"Error: {e}")
        return -2, 0
    return -2, 0

def main():
    opponents = [
        'tournament_bots/simple_bot.py',
        'tournament_bots/viper.py',
        'tournament_bots/fortress.py',
        'tournament_bots/agent_v1_95pc.py',
        'tournament_bots/agent_v2_timesplit.py'
    ]
    my_agent = 'agent.py'
    seeds = [100 + i * 17 for i in range(10)]
    
    total_wins = 0
    total_draws = 0
    total_losses = 0
    
    losses_details = []

    print("==========================================================================")
    print(" SELF-EVOLUTION & REGRESSION TOURNAMENT SUITE (100 MATCHES)")
    print("==========================================================================")

    for opp in opponents:
        opp_name = os.path.basename(opp)
        print(f"\n--- Testing agent.py vs {opp_name} ---")
        
        # Test as P0
        for s in seeds:
            w, steps = run_single_match(my_agent, opp, s)
            if w == 0:
                total_wins += 1
                print(f"  Seed {s:3d} (as P0): WIN in {steps} steps")
            elif w == 1:
                total_losses += 1
                print(f"  Seed {s:3d} (as P0): LOSS to {opp_name} in {steps} steps!")
                losses_details.append(('P0', opp_name, s, steps))
            else:
                total_draws += 1
                print(f"  Seed {s:3d} (as P0): DRAW in {steps} steps")

        # Test as P1
        for s in seeds:
            w, steps = run_single_match(opp, my_agent, s)
            if w == 1:
                total_wins += 1
                print(f"  Seed {s:3d} (as P1): WIN in {steps} steps")
            elif w == 0:
                total_losses += 1
                print(f"  Seed {s:3d} (as P1): LOSS to {opp_name} in {steps} steps!")
                losses_details.append(('P1', opp_name, s, steps))
            else:
                total_draws += 1
                print(f"  Seed {s:3d} (as P1): DRAW in {steps} steps")

    print("\n==========================================================================")
    print(f" EVOLUTION SUMMARY: Wins={total_wins}, Losses={total_losses}, Draws={total_draws}")
    print(f" Overall Win Rate: {total_wins / (total_wins + total_losses + total_draws) * 100:.1f}%")
    print("==========================================================================")
    
    if losses_details:
        print("\nLoss Details for Self-Improvement Analysis:")
        for role, opp, s, st in losses_details:
            print(f" - Role {role} vs {opp} on Seed {s} (Steps {st})")

if __name__ == '__main__':
    main()
