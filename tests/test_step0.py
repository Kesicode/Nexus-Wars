import json
import subprocess

def test_step0_launch():
    # Synthetic observation at Step 0
    obs = {
        "player": 0,
        "step": 0,
        "angular_velocity": 0.035,
        "planets": [
            [0, 0, 65.0, 68.0, 1.69, 10, 2, 85, 100, 5],
            [1, -1, 72.0, 76.0, 1.69, 6, 4, 0, 100, 5],
            [2, 1, 35.0, 35.0, 1.69, 10, 2, 85, 100, 5]
        ],
        "fleets": [],
        "initial_planets": [
            [0, 0, 65.0, 68.0, 1.69, 10, 2, 85, 100, 5],
            [1, -1, 72.0, 76.0, 1.69, 6, 4, 0, 100, 5],
            [2, 1, 35.0, 35.0, 1.69, 10, 2, 85, 100, 5]
        ]
    }
    proc = subprocess.Popen(['python', 'agent.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    out, _ = proc.communicate(input=json.dumps(obs) + "\n")
    actions = json.loads(out.strip())
    assert len(actions) > 0, "Agent failed to launch on Step 0!"
    from_id, angle, ships = actions[0]
    assert from_id == 0, f"Expected launch from planet 0, got {from_id}"
    assert ships >= 5, f"Expected launch of at least 5 ships, got {ships}"
    print("Step 0 test passed!")

if __name__ == "__main__":
    test_step0_launch()
