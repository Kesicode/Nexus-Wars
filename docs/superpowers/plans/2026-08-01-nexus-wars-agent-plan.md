# Nexus Wars Hybrid Dominance Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade `agent.py` to incorporate Step-0 opening launches, predictive unlaunched enemy threat defense, smart planet evacuation, and 12.0-unit Sun clearance safety margin to achieve a 100% tournament win rate.

**Architecture:** Enhances `NexusAgent` in `agent.py` across 4 key decision layers: Step-0 opening dispatch, predictive enemy energy threat calculations, flight evacuation for doomed planets, and strict segment-Sun safety geometry.

**Tech Stack:** Python 3.12, StdLib (math, json, sys), Numpy, Nexus Wars Simulator harness (`reference/main.py`).

## Global Constraints

- Runtime constraint: $< 1000 \text{ ms}$ per step inside sandbox (target $< 50 \text{ ms}$).
- Memory budget: $< 512 \text{ MB}$ RAM.
- Dependencies: StdLib + `numpy` only.
- Board geometry: 100.0 x 100.0 continuous 2D space, Sun at (50, 50) radius 10.0.

---

### Task 1: Step-0 Instant Opening & Rapid Re-launch Pipeline

**Files:**
- Modify: `c:/Users/kesi/Downloads/aiagent-main/agent.py:330-342, 480-575`
- Test: `c:/Users/kesi/Downloads/aiagent-main/test_step0.py`

**Interfaces:**
- Consumes: `obs["planets"]`, `obs["step"]`, `obs["player"]`
- Produces: `actions` list with Step-0 launch `[[src_id, angle, ships]]`

- [ ] **Step 1: Write failing test for Step-0 launch**

Create `test_step0.py`:
```python
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
    assert ships >= 6, f"Expected launch of at least 6 ships, got {ships}"
    print("Step 0 test passed!")

if __name__ == "__main__":
    test_step0_launch()
```

- [ ] **Step 2: Run test to verify current agent behavior**

Run: `python test_step0.py`
Expected: Failure if current `agent.py` `min_launch` or `min_keep` blocks Step 0 launch.

- [ ] **Step 3: Modify `agent.py` to enable Step-0 launch and tuned target scoring**

In `agent.py`:
1. In `min_keep` calculation: for `step == 0`, set `min_keep[home_id] = 2` so 8 ships are available.
2. In Layer 3 (Neutral Expansion): for `step == 0`, set `min_launch = 5`.
3. Update neutral scoring formula for step 0:
   `score = t_prod * 60 - distance(src_pos, target_pos) * 1.2 - future_garrison * 0.5`

- [ ] **Step 4: Run test to verify it passes**

Run: `python test_step0.py`
Expected: `Step 0 test passed!`

- [ ] **Step 5: Commit**

```bash
git add agent.py test_step0.py
git commit -m "feat: enable Step-0 instant opening launch and tuned target scoring"
```

---

### Task 2: Predictive Enemy Launch Threat & Dynamic Defense Guard

**Files:**
- Modify: `c:/Users/kesi/Downloads/aiagent-main/agent.py:305-340`
- Test: `c:/Users/kesi/Downloads/aiagent-main/test_threat.py`

**Interfaces:**
- Consumes: `enemy_planets`, `my_planets`
- Produces: Dynamic `min_keep[pid]` defense thresholds based on unlaunched enemy energy pools.

- [ ] **Step 1: Write failing test for unlaunched threat guard**

Create `test_threat.py`:
```python
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
    # Run act
    actions = agent.act(obs)
    # Ensure agent doesn't send ALL ships away, reserving at least 15+ for incoming potential threat
    if actions:
        sent = sum(a[2] for a in actions if a[0] == 0)
        assert 30 - sent >= 12, f"Left too few ships ({30 - sent}) against high-energy enemy!"
    print("Unlaunched threat test passed!")

if __name__ == "__main__":
    test_unlaunched_threat()
```

- [ ] **Step 2: Run test to verify current behavior**

Run: `python test_threat.py`
Expected: Verify behavior against high-energy enemy.

- [ ] **Step 3: Implement unlaunched threat calculation in `agent.py`**

Add threat modeling helper in `NexusAgent`:
```python
def get_unlaunched_enemy_threat(self, target_pos, enemy_planets):
    max_threat = 0
    for ep in enemy_planets:
        e_val = ep[7]
        e_ships = ep[5]
        if e_val >= 20 and e_ships > 15:
            d = distance(target_pos, (ep[2], ep[3]))
            if d < 35.0:
                threat_ships = e_ships - 5
                weight = (35.0 - d) / 35.0
                max_threat = max(max_threat, threat_ships * weight)
    return max_threat
```

Integrate into `min_keep` calculation:
`min_keep[pid] = max(min_keep[pid], int(unlaunched_threat * 0.4))`

- [ ] **Step 4: Run test to verify it passes**

Run: `python test_threat.py`
Expected: `Unlaunched threat test passed!`

- [ ] **Step 5: Commit**

```bash
git add agent.py test_threat.py
git commit -m "feat: implement predictive unlaunched enemy energy threat defense guard"
```

---

### Task 3: Evacuation Engine ("Flight Strategy") for Doomed Planets

**Files:**
- Modify: `c:/Users/kesi/Downloads/aiagent-main/agent.py:350-428`
- Test: `c:/Users/kesi/Downloads/aiagent-main/test_evacuation.py`

**Interfaces:**
- Consumes: `threatened_planets`, `reserves`, `my_planets`
- Produces: Evacuation action `[[doomed_pid, angle_to_safe_target, all_garrison]]`

- [ ] **Step 1: Write test for planet evacuation**

Create `test_evacuation.py`:
```python
import json
from agent import NexusAgent

def test_evacuation():
    agent = NexusAgent()
    # Planet 0 is threatened by 100 incoming enemy ships in 5 steps.
    # We have Planet 0 with 25 ships, and Planet 1 (safe) with 20 ships.
    # Planet 0 cannot be saved. It should evacuate all 25 ships to Planet 1.
    obs = {
        "player": 0,
        "step": 30,
        "angular_velocity": 0.035,
        "planets": [
            [0, 0, 20.0, 20.0, 1.69, 25, 2, 80, 100, 5],
            [1, 0, 80.0, 80.0, 1.69, 20, 3, 80, 100, 5],
            [2, 1, 20.0, 80.0, 1.69, 50, 4, 80, 100, 5]
        ],
        "fleets": [
            [101, 1, 20.0, 35.0, -1.5708, 2, 100, 28] # incoming fleet to planet 0
        ],
        "initial_planets": [
            [0, 0, 20.0, 20.0, 1.69, 25, 2, 80, 100, 5],
            [1, 0, 80.0, 80.0, 1.69, 20, 3, 80, 100, 5],
            [2, 1, 20.0, 80.0, 1.69, 50, 4, 80, 100, 5]
        ]
    }
    actions = agent.act(obs)
    # Check if planet 0 evacuated
    p0_evac = [a for a in actions if a[0] == 0]
    assert len(p0_evac) > 0, "Doomed planet failed to evacuate!"
    assert p0_evac[0][2] >= 20, f"Expected full evacuation of ships, sent {p0_evac[0][2]}"
    print("Evacuation test passed!")

if __name__ == "__main__":
    test_evacuation()
```

- [ ] **Step 2: Run test to verify current behavior**

Run: `python test_evacuation.py`

- [ ] **Step 3: Implement Evacuation Engine in Layer 1 of `agent.py`**

In Layer 1 (Defense Strategy):
When `total_possible < needed` and `target_id != self.home_planet_id`:
```python
# Evacuate doomed planet
doomed_planet = next((p for p in my_planets if p[0] == target_id), None)
if doomed_planet and temp_energy[target_id] >= LAUNCH_COST:
    avail_evac = temp_ships[target_id]
    if avail_evac >= 5:
        # Find safest friendly high-prod planet or safe neutral
        safe_targets = [p for p in my_planets if p[0] != target_id]
        if safe_targets:
            best_safe = max(safe_targets, key=lambda p: p[6])
            angle = math.atan2(best_safe[3] - doomed_planet[3], best_safe[2] - doomed_planet[2])
            if not path_crosses_sun((doomed_planet[2], doomed_planet[3]), (best_safe[2], best_safe[3])):
                actions.append([target_id, angle, avail_evac])
                temp_ships[target_id] = 0
                temp_energy[target_id] -= LAUNCH_COST
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python test_evacuation.py`
Expected: `Evacuation test passed!`

- [ ] **Step 5: Commit**

```bash
git add agent.py test_evacuation.py
git commit -m "feat: implement evacuation engine for doomed planets"
```

---

### Task 4: Enhanced Sun Clearance Safety Buffer (12.0 Units)

**Files:**
- Modify: `c:/Users/kesi/Downloads/aiagent-main/agent.py:10-15, 345-347`
- Test: `c:/Users/kesi/Downloads/aiagent-main/test_sun_margin.py`

**Interfaces:**
- Consumes: Fleet segment geometry
- Produces: `SUN_SAFE_RADIUS = 12.0` enforcement in `path_crosses_sun` and raycasting checks.

- [ ] **Step 1: Write test for Sun margin clearance**

Create `test_sun_margin.py`:
```python
from agent import path_crosses_sun, SUN_SAFE_RADIUS

def test_sun_margin():
    assert SUN_SAFE_RADIUS >= 12.0, f"Expected SUN_SAFE_RADIUS >= 12.0, got {SUN_SAFE_RADIUS}"
    # Segment passing at distance 11.0 from (50, 50)
    src = (50.0, 20.0)
    dst = (50.0, 80.0) # passes through center (50, 50) -> dist = 0 < 12.0
    assert path_crosses_sun(src, dst) == True
    print("Sun margin test passed!")

if __name__ == "__main__":
    test_sun_margin()
```

- [ ] **Step 2: Run test to verify**

Run: `python test_sun_margin.py`

- [ ] **Step 3: Update `SUN_SAFE_RADIUS` in `agent.py` to 12.0**

In `agent.py`:
`SUN_SAFE_RADIUS = 12.0`

- [ ] **Step 4: Run test to verify it passes**

Run: `python test_sun_margin.py`

- [ ] **Step 5: Commit**

```bash
git add agent.py test_sun_margin.py
git commit -m "fix: increase Sun safety clearance buffer to 12.0 units"
```

---

### Task 5: End-to-End Tournament Benchmark Verification

**Files:**
- Test: `c:/Users/kesi/Downloads/aiagent-main/run_tournament.py`

- [ ] **Step 1: Run full tournament across all seeds**

Run: `python run_tournament.py`

- [ ] **Step 2: Verify 100% Win Rate & 0 Sun Deaths**

Check tournament standings output:
Expected: `agent.py` 15 wins, 0 losses, 45 points (100% win rate).

- [ ] **Step 3: Final Commit**

```bash
git add agent.py
git commit -m "chore: complete Nexus Wars Hybrid Dominance Engine implementation"
```
