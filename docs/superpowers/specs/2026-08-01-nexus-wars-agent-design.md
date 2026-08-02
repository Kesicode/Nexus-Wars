# Nexus Wars AI Agent: Hybrid Dominance Engine Design Specification

## Executive Summary
This document outlines the architectural design for the **Nexus Wars Hybrid Dominance Engine** (`agent.py`), designed to compete and achieve top rank in the deterministic 1v1 RTS environment.

Incorporating empirical insights from the top winning match replays in the user's `Report` dataset (`match-4273ee13`, `match-85346b21`, `match-fa557aaa`, `match-fe91be26`), this specification elevates the bot architecture to guarantee 100% win-rate dominance.

Key empirical discoveries from report replays:
1. **Step-0 Instant Launch**: Dominant bots *always* launch on Step 0 (starting energy is 85, launch cost 20).
2. **Opening Fleet Sizing**: Sending $F = \text{garrison} + 2$ (typically 7 to 10 ships) on Step 0 captures target neutrals up to 3 turns earlier than waiting for large fleets.
3. **High-Production Priority**: Targeting high-production neutrals ($\text{prod} \ge 4$ or $\ge 3$) closest to home.
4. **Predictive Enemy Launch Guard**: Preventing home/frontline planet captures by anticipating unlaunched enemy energy pools.
5. **Evacuation Engine ("Flight Strategy")**: Evacuate doomed planets to preserve total ship mass for counter-attacks.

---

## Strategic Architecture & System Components

```
+-------------------------------------------------------------------------+
|                              NexusAgent                                 |
+-------------------------------------------------------------------------+
                                    |
   +--------------------------------+--------------------------------+
   |                                |                                |
   v                                v                                v
[ 1. Step-0 Instant Opening ]   [ 2. Predictive Threat ]   [ 3. Evacuation Engine ]
[    & Rapid Re-launch      ]   [    & Defense Guard   ]   [    ("Flight Strategy")]
   |                                |                                |
   +--------------------------------+--------------------------------+
                                    |
                                    v
                     [ 4. Forward Simulator (80 Steps) ]
                     [    & Sun Clearance (12.0 Margin)  ]
```

### Component 1: Step-0 Instant Opening & Rapid Re-launch Pipeline
- **Step 0 Launch Guarantee**: Set Step 0 launch minimum threshold to $5$ ships (instead of 8 or 12).
- **Target Selection**:
  - Identify neutral planet $p^*$ maximizing:
    $$\text{Score}(p) = \text{prod} \times 60 - \text{distance} \times 1.2 - \text{garrison} \times 0.5$$
  - Send $F_{\text{launch}} = \max(6, \text{garrison}(p^*) + 2)$ ships on Step 0.
- **Continuous Re-launch Cadence**: Re-evaluating energy every turn step. Once energy $\ge 20$, immediately dispatch expansion/reinforcement fleets if `avail_ships >= min_launch`.

### Component 2: Predictive Threat & Dynamic Defense Guard
- **Unlaunched Energy Threat Modeling**: For every enemy planet with energy $\ge 20$ and garrison $G > 15$, compute the maximum fleet size $F_{\text{enemy}} = G - 5$ that could be launched against each of our planets.
- **Dynamic `min_keep` Base**:
  $$\text{min\_keep}[p] = \max\left(\text{static\_danger}, \min(40, \text{enemy\_threat\_potential} \times 0.7)\right)$$
- **Home Planet Hard Fortress**: Maintain a minimum garrison floor on home planet scaling with enemy proximity and enemy energy reserves.

### Component 3: Smart Evacuation ("Fight vs Flight")
- If an owned planet is predicted to fall to an incoming enemy force within $T$ steps, and friendly reserves cannot arrive in time to save it:
  - Immediately launch all available garrison ships (leaving 0) toward the nearest friendly high-production planet or a safe neutral expansion target.
  - Deny ship kills to the enemy and preserve fleet mass for counter-strikes.

### Component 4: Coordinated Multi-Wave Assaults
- **Synchronized Wave Launches**:
  - Target highest-value enemy/neutral planets.
  - Solve for launch steps across multiple planets such that fleets moving at logarithmic speeds $v(S) = \min(6.0, 1.0 + 5.0(\frac{\ln S}{\ln 1000})^{1.5})$ land on the **exact same step** $t_{\text{arr}}$.

### Component 5: Sun Clearance & Physics Precision
- Point-to-segment distance to Sun center $(50, 50)$ enforced with a safety threshold of $12.0$ units ($10.0$ Sun radius + $2.0$ margin).
- Swept-pair continuous collision check over line segments.

---

## Verification Plan

### Automated Benchmarks
1. Run tournament evaluation against baseline bots (`simple_bot.py`, `viper.py`, `fortress.py`) across 10 distinct seeds.
2. Target Criteria:
   - Win rate: 100% (30/30 matches won).
   - Sun vaporizations: 0.
   - Per-step compute time: $< 100 \text{ ms}$ (well below 1000 ms sandbox limit).

---

## Design Review Status
- **Status**: Draft - Updated with Report Replay Insights. Awaiting User Approval.
