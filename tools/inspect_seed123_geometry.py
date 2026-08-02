import json
import subprocess
import math

def main():
    # Run match on seed 123: Player 0 = simple_bot, Player 1 = agent.py
    cmd = [
        'python', 'reference/main.py',
        '--agents', 'python tournament_bots/simple_bot.py', 'python agent.py',
        '--seed', '123',
        '--out', 'seed123_geo.json'
    ]
    subprocess.run(cmd, capture_output=True, text=True)
    
    with open('seed123_geo.json', 'r') as f:
        data = json.load(f)
        
    obs = data['steps'][0]['observation']
    planets = obs['planets']
    angular_vel = obs.get('angular_velocity', 0.035)
    
    print(f"Seed 123 Angular Velocity: {angular_vel}")
    print(f"Total Planets: {len(planets)}")
    
    p0_home = [p for p in planets if p[1] == 0][0]
    p1_home = [p for p in planets if p[1] == 1][0]
    neutrals = [p for p in planets if p[1] == -1]
    
    print(f"P0 Home (ID {p0_home[0]}): Pos ({p0_home[2]:.1f}, {p0_home[3]:.1f}), Prod {p0_home[6]}, Radius {p0_home[4]:.2f}")
    print(f"P1 Home (ID {p1_home[0]}): Pos ({p1_home[2]:.1f}, {p1_home[3]:.1f}), Prod {p1_home[6]}, Radius {p1_home[4]:.2f}")
    
    print("\n--- Neutrals sorted by distance to P1 Home ---")
    for p in neutrals:
        d_p0 = math.sqrt((p[2]-p0_home[2])**2 + (p[3]-p0_home[3])**2)
        d_p1 = math.sqrt((p[2]-p1_home[2])**2 + (p[3]-p1_home[3])**2)
        print(f"Neutral ID {p[0]:2d}: Pos ({p[2]:4.1f}, {p[3]:4.1f}), Prod {p[6]}, Garrison {p[5]:2d} | Dist to P0: {d_p0:4.1f}, Dist to P1: {d_p1:4.1f}")

if __name__ == '__main__':
    main()
