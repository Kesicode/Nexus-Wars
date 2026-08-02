import json
import glob

def inspect_p1_losses():
    files = glob.glob("Report/*.json")
    
    print("=== INSPECTING MATCHES WHERE P1 LOST (P0 WON) ===")
    p1_losses = []
    
    for fpath in files:
        with open(fpath, 'r') as f:
            data = json.load(f)
            
        info = data.get("info", {})
        winner = info.get("winner", -1)
        
        if winner == 0:
            steps = data.get("steps", [])
            p0_planets_captured = 0
            p1_planets_captured = 0
            
            # Check step 0
            s0_acts = steps[0].get("action", [])
            p0_s0 = s0_acts[0] if len(s0_acts) > 0 else []
            p1_s0 = s0_acts[1] if len(s0_acts) > 1 else []
            
            p1_losses.append({
                "file": fpath,
                "steps": len(steps),
                "scores": info.get("scores", [0, 0]),
                "p0_s0": p0_s0,
                "p1_s0": p1_s0
            })
            
    print(f"Total P1 losses (P0 wins): {len(p1_losses)}")
    print("\nSample 5 P1 Losses:")
    for item in p1_losses[:5]:
        print(f"File: {item['file']}")
        print(f"  P0 Step 0: {item['p0_s0']}")
        print(f"  P1 Step 0: {item['p1_s0']}")
        print(f"  Scores: {item['scores']}")

if __name__ == '__main__':
    inspect_p1_losses()
