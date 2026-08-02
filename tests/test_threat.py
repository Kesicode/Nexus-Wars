from agent import NexusAgent

def test_unlaunched_threat():
    agent = NexusAgent()
    # Enemy has 100 energy and 50 ships 20 units away
    obs = {
        "player": 0,
        "step": 10,
        "angular_velocity": 0.035,
        "planets": [
            [0, 0, 50.0, 20.0, 1.69, 30, 2, 80, 100, 5],
            [1, 1, 50.0, 35.0, 1.69, 50, 4, 100, 100, 5]
        ],
        "fleets": [],
        "initial_planets": [
            [0, 0, 50.0, 20.0, 1.69, 30, 2, 80, 100, 5],
            [1, 1, 50.0, 35.0, 1.69, 50, 4, 100, 100, 5]
        ]
    }
    actions = agent.act(obs)
    if actions:
        sent = sum(a[2] for a in actions if a[0] == 0)
        # Ensure we keep sufficient defense against unlaunched 50-ship enemy
        assert 30 - sent >= 10, f"Left too few ships ({30 - sent}) against high-energy enemy!"
    print("Unlaunched threat test passed!")

if __name__ == "__main__":
    test_unlaunched_threat()
