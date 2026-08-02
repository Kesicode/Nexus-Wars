import json

def main():
    with open('loss_seed185.json', 'r') as f:
        data = json.load(f)
        
    steps = data['steps']
    
    print("=== SEED 185 DIAGNOSTIC TRACE vs VIPER.PY ===")
    for s in range(0, 150, 5):
        obs = steps[s]['observation']
        actions = steps[s].get('actions', [])
        p0_p = [p for p in obs['planets'] if p[1] == 0]
        p1_p = [p for p in obs['planets'] if p[1] == 1]
        
        p0_f = [f for f in obs.get('fleets', []) if f[1] == 0]
        p1_f = [f for f in obs.get('fleets', []) if f[1] == 1]
        p0_ships = sum(p[5] for p in p0_p) + sum(f[6] for f in p0_f)
        p1_ships = sum(p[5] for p in p1_p) + sum(f[6] for f in p1_f)

        act_str = ""
        if len(actions) > 0 and actions[0]:
            act_str += f" P0(viper)_act: {actions[0]}"
        if len(actions) > 1 and actions[1]:
            act_str += f" P1(agent)_act: {actions[1]}"
            
        print(f"Step {s:3d} | P0(viper): {len(p0_p):2d} plan, {p0_ships:4d} shp | P1(agent): {len(p1_p):2d} plan, {p1_ships:4d} shp |{act_str}")

if __name__ == '__main__':
    main()
