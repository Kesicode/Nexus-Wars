import json

def main():
    with open('seed123_test.json', 'r') as f:
        data = json.load(f)
        
    steps = data['steps']
    
    for s in range(40, 130):
        obs = steps[s]['observation']
        actions = steps[s].get('actions', [])
        p0_p = [p for p in obs['planets'] if p[1] == 0]
        p1_p = [p for p in obs['planets'] if p[1] == 1]
        
        # Check fleet ship totals
        p0_f = [f for f in obs.get('fleets', []) if f[1] == 0]
        p1_f = [f for f in obs.get('fleets', []) if f[1] == 1]
        p0_ships = sum(p[5] for p in p0_p) + sum(f[6] for f in p0_f)
        p1_ships = sum(p[5] for p in p1_p) + sum(f[6] for f in p1_f)

        act_str = ""
        if len(actions) > 0 and actions[0]:
            act_str += f" P0_act: {actions[0]}"
        if len(actions) > 1 and actions[1]:
            act_str += f" P1_act: {actions[1]}"
            
        print(f"Step {s:3d} | P0(simple): {len(p0_p):2d} plan, {p0_ships:4d} shp | P1(agent): {len(p1_p):2d} plan, {p1_ships:4d} shp |{act_str}")

if __name__ == '__main__':
    main()
