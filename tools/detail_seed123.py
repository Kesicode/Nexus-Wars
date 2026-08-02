import json

def main():
    with open('seed123_defeat.json', 'r') as f:
        replay = json.load(f)

    steps = replay['steps']
    
    for s in range(60, 130):
        obs_curr = steps[s]['observation']
        p1_planets = [p for p in obs_curr['planets'] if p[1] == 1]
        p0_planets = [p for p in obs_curr['planets'] if p[1] == 0]
        
        # Look for planet ownership changes
        if s > 0:
            obs_prev = steps[s-1]['observation']
            prev_dict = {p[0]: p[1] for p in obs_prev['planets']}
            curr_dict = {p[0]: p[1] for p in obs_curr['planets']}
            for pid, curr_owner in curr_dict.items():
                prev_owner = prev_dict.get(pid, -1)
                if prev_owner != curr_owner:
                    print(f"Step {s:3d}: Planet {pid:2d} changed owner from {prev_owner} to {curr_owner}!")

if __name__ == '__main__':
    main()
