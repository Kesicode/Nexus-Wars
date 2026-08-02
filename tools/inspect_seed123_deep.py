import json

def main():
    with open('seed123_test3.json', 'r') as f:
        data = json.load(f)
        
    steps = data['steps']
    
    print("=== SEED 123 MIDGAME PLANET LOSSES ===")
    for s in range(40, 150):
        obs_prev = steps[s-1]['observation']
        obs_curr = steps[s]['observation']
        actions = steps[s].get('actions', [])
        
        p0_act = actions[0] if len(actions) > 0 else []
        p1_act = actions[1] if len(actions) > 1 else []
        
        prev_dict = {p[0]: p[1] for p in obs_prev['planets']}
        curr_dict = {p[0]: p[1] for p in obs_curr['planets']}
        
        for pid, curr_owner in curr_dict.items():
            prev_owner = prev_dict.get(pid, -1)
            if prev_owner != curr_owner:
                p_info = [p for p in obs_curr['planets'] if p[0] == pid][0]
                print(f"Step {s:3d}: Planet {pid:2d} (Prod {p_info[6]}, Garrison {p_info[5]}) CHANGED OWNER from {prev_owner} to {curr_owner}!")

if __name__ == '__main__':
    main()
