import json

def main():
    with open('seed123_test5.json', 'r') as f:
        data = json.load(f)
        
    steps = data['steps']
    
    for s in range(30, 90, 2):
        obs = steps[s]['observation']
        actions = steps[s].get('actions', [])
        p0_p = [p for p in obs['planets'] if p[1] == 0]
        p1_p = [p for p in obs['planets'] if p[1] == 1]
        
        act_str = ""
        if len(actions) > 0 and actions[0]:
            act_str += f" P0_act: {actions[0]}"
        if len(actions) > 1 and actions[1]:
            act_str += f" P1_act: {actions[1]}"
            
        print(f"Step {s:3d} | P0(simple): {len(p0_p):2d} plan | P1(agent): {len(p1_p):2d} plan |{act_str}")

if __name__ == '__main__':
    main()
