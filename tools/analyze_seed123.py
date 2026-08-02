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
    with open('seed123_defeat.json', 'r') as f:
        replay = json.load(f)

    steps = replay['steps']
    
    sun_deaths = 0
    for s in range(1, len(steps)):
        obs_prev = steps[s-1]['observation']
        obs_curr = steps[s]['observation']
        
        fleets_prev = {f[0]: f for f in obs_prev.get('fleets', [])}
        fleets_curr = {f[0]: f for f in obs_curr.get('fleets', [])}
        
        for fid, f in fleets_prev.items():
            if fid not in fleets_curr:
                # Fleet disappeared between step s-1 and step s
                # Check if it hit a planet or Sun
                owner = f[1]
                x0, y0 = f[2], f[3]
                angle = f[4]
                ships = f[6]
                spd = fleet_speed(ships)
                x1 = x0 + math.cos(angle) * spd
                y1 = y0 + math.sin(angle) * spd
                
                sun_d = point_to_segment_distance((50.0, 50.0), (x0, y0), (x1, y1))
                if sun_d < SUN_RADIUS:
                    print(f"Step {s}: Fleet {fid} (Owner {owner}, ships {ships}) VAPORIZED BY SUN! dist={sun_d:.2f}")
                    if owner == 1:
                        sun_deaths += 1

    print(f"Total P1 fleets vaporized by Sun: {sun_deaths}")

if __name__ == '__main__':
    main()
