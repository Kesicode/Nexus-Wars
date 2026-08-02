import json
import os
import glob
import math

def dist(ax, ay, bx, by):
    return math.sqrt((ax - bx)**2 + (ay - by)**2)

def analyze_step0_targets(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    steps = data.get('steps', [])
    if not steps:
        return
        
    obs = steps[0]['observation']
    planets = obs.get('planets', [])
    p0_home = [p for p in planets if p[1] == 0][0]
    p0_x, p0_y = p0_home[2], p0_home[3]
    
    act = steps[0].get('action', [])
    print(f"\nFile: {os.path.basename(filepath)}")
    print(f"P0 Home Planet: ID {p0_home[0]}, Pos ({p0_x:.1f}, {p0_y:.1f}), Garrison {p0_home[5]}, Energy {p0_home[7]}")
    
    if act and isinstance(act, list) and len(act) > 0:
        p0_move = act[0]
        print(f"P0 Step 0 Move: {p0_move}")
        if p0_move:
            for move in p0_move:
                from_id, angle, ships = move
                # Calculate ray direction
                dx = math.cos(angle)
                dy = math.sin(angle)
                # Find closest planet along this angle
                closest_p = None
                closest_dist = float('inf')
                for p in planets:
                    if p[0] == p0_home[0]:
                        continue
                    px, py = p[2], p[3]
                    v_x, v_y = px - p0_x, py - p0_y
                    d = math.sqrt(v_x**2 + v_y**2)
                    # Dot product with angle vector
                    dot = (v_x * dx + v_y * dy) / d
                    if dot > 0.95 and d < closest_dist:
                        closest_dist = d
                        closest_p = p
                if closest_p:
                    print(f"  Target Planet ID {closest_p[0]}: Pos ({closest_p[2]:.1f}, {closest_p[3]:.1f}), Prod {closest_p[6]}, Garrison {closest_p[5]}, Dist {closest_dist:.1f}")

if __name__ == '__main__':
    for f in sorted(glob.glob('Report/*.json')):
        analyze_step0_targets(f)
