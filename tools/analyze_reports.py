import json
import os
import glob
import math

def analyze_match(filepath):
    print(f"\n==================================================")
    print(f" ANALYZING REPORT MATCH: {os.path.basename(filepath)}")
    print(f"==================================================")
    
    with open(filepath, 'r') as f:
        data = json.load(f)
        
    seed = data.get('seed')
    players = data.get('players', [])
    info = data.get('info', {})
    
    print(f"Seed: {seed}")
    print(f"Players: {players}")
    print(f"Match Info: {info}")
    
    steps = data.get('steps', [])
    print(f"Total Steps: {len(steps)}")
    if not steps:
        return

    first_obs = steps[0]['observation']
    init_planets = first_obs.get('planets', [])
    print(f"Initial Total Planets: {len(init_planets)}")
    
    p0_actions = []
    p1_actions = []
    
    # Collect all actions taken by P0 and P1
    for s_idx, s in enumerate(steps):
        act = s.get('action') # list of moves for the player whose turn/step it is, or dict
        # In Kaggle/nsjail format, action can be [player0_moves, player1_moves] or similar
        if act and isinstance(act, list):
            # If length is 2 and first elem is list, it's [p0_moves, p1_moves]
            if len(act) == 2 and isinstance(act[0], list):
                if act[0]:
                    p0_actions.append((s_idx, act[0]))
                if act[1]:
                    p1_actions.append((s_idx, act[1]))
            else:
                # Single player move list or tuple
                pass

    print(f"\nP0 Total Action Turns: {len(p0_actions)}")
    print(f"P1 Total Action Turns: {len(p1_actions)}")
    
    print("\n--- P0 (Dominant Winner) Opening Moves (Steps 0-30) ---")
    for s_idx, moves in p0_actions:
        if s_idx <= 30:
            print(f"  Step {s_idx:2d}: {moves}")
            
    print("\n--- P1 Opening Moves (Steps 0-30) ---")
    for s_idx, moves in p1_actions:
        if s_idx <= 30:
            print(f"  Step {s_idx:2d}: {moves}")

if __name__ == '__main__':
    report_files = sorted(glob.glob('Report/*.json'))
    for f in report_files:
        analyze_match(f)
