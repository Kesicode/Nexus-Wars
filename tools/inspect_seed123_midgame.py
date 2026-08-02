import json
import math

SUN_X, SUN_Y = 50.0, 50.0
SUN_RADIUS = 10.0

def dist(ax, ay, bx, by):
    return math.sqrt((ax - bx)**2 + (ay - by)**2)

def point_to_segment_distance(p, v, w):
    l2 = (v[0] - w[0]) ** 2 + (v[1] - w[1]) ** 2
    if l2 == 0.0:
        return dist(p[0], p[1], v[0], v[1])
    t = max(0, min(1, ((p[0] - v[0]) * (w[0] - v[0]) + (p[1] - v[1]) * (w[1] - v[1])) / l2))
    projection = (v[0] + t * (w[0] - v[0]), v[1] + t * (w[1] - v[1]))
    return dist(p[0], p[1], projection[0], projection[1])

def fleet_speed(ships):
    if ships <= 0:
        return 0
    return min(6.0, 1.0 + 5.0 * (math.log(max(ships, 1)) / math.log(1000)) ** 1.5)

def main():
    with open('seed123_test.json', 'r') as f:
        data = json.load(f)
        
    steps = data['steps']
    
    for s in range(80, 115):
        obs_curr = steps[s]['observation']
        actions = steps[s].get('actions', [])
        p1_act = actions[1] if len(actions) > 1 else None
        
        if p1_act:
            print(f"Step {s:3d}: P1 launched actions: {p1_act}")
            
        # Check fleets disappearing
        if s > 0:
            obs_prev = steps[s-1]['observation']
            f_prev = {f[0]: f for f in obs_prev.get('fleets', []) if f[1] == 1}
            f_curr = {f[0]: f for f in obs_curr.get('fleets', []) if f[1] == 1}
            
            for fid, f in f_prev.items():
                if fid not in f_curr:
                    x0, y0 = f[2], f[3]
                    angle = f[4]
                    ships = f[6]
                    spd = fleet_speed(ships)
                    x1 = x0 + math.cos(angle) * spd
                    y1 = y0 + math.sin(angle) * spd
                    
                    sun_d = point_to_segment_distance((50.0, 50.0), (x0, y0), (x1, y1))
                    print(f"  Step {s:3d}: P1 Fleet {fid} ({ships} ships from planet {f[5]}) disappeared! (Sun dist={sun_d:.2f})")

if __name__ == '__main__':
    main()
