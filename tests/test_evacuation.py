import json
from agent import NexusAgent

def test_evacuation():
    agent = NexusAgent()
    # Planet 1 is home planet at (20, 60). Planet 0 is static outer secondary planet at (10, 10).
    # Path from (10, 10) to (20, 60) stays along x=10..20, far away from Sun at (50, 50).
    # Planet 0 is threatened by 100 incoming enemy ships in 4 steps.
    # Planet 0 cannot be saved. It should evacuate all garrison ships to Planet 1.
    obs = {
        "player": 0,
        "step": 30,
        "angular_velocity": 0.035,
        "planets": [
            [1, 0, 20.0, 60.0, 1.69, 20, 3, 80, 100, 5], # Home planet (first in list)
            [0, 0, 10.0, 10.0, 1.69, 25, 2, 80, 100, 5], # Outer static secondary planet (r >= 50)
            [2, 1, 10.0, 80.0, 1.69, 50, 4, 80, 100, 5]
        ],
        "fleets": [
            [101, 1, 10.0, 25.0, -1.5708, 2, 100, 28] # incoming fleet to planet 0
        ],
        "initial_planets": [
            [1, 0, 20.0, 60.0, 1.69, 20, 3, 80, 100, 5],
            [0, 0, 10.0, 10.0, 1.69, 25, 2, 80, 100, 5],
            [2, 1, 10.0, 80.0, 1.69, 50, 4, 80, 100, 5]
        ]
    }
    actions = agent.act(obs)
    p0_evac = [a for a in actions if a[0] == 0]
    assert len(p0_evac) > 0, "Doomed planet failed to evacuate!"
    assert p0_evac[0][2] >= 20, f"Expected full evacuation of ships, sent {p0_evac[0][2]}"
    print("Evacuation test passed!")

if __name__ == "__main__":
    test_evacuation()
