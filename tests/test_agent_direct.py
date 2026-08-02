import json
import subprocess
import time
import sys

def main():
    replay_path = 'c:/Users/USER/OneDrive/Desktop/aibot/replay.json'
    with open(replay_path, 'r') as f:
        replay = json.load(f)

    # Start agent.py as a subprocess
    proc = subprocess.Popen(
        ['python', 'c:/Users/USER/OneDrive/Desktop/aibot/agent.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    steps = replay['steps']
    print(f"Feeding {len(steps)} steps sequentially to agent.py...")

    for idx, step_data in enumerate(steps):
        obs = step_data['observation']
        obs['player'] = 0  # ensure player is 0

        t0 = time.perf_counter()
        try:
            proc.stdin.write(json.dumps(obs) + "\n")
            proc.stdin.flush()
            
            # Read stdout line
            line = proc.stdout.readline()
            duration = (time.perf_counter() - t0) * 1000  # ms
            
            if duration > 100:
                print(f"Warning: Step {idx} took {duration:.2f} ms")
            if duration > 150:
                print(f"TIMEOUT EXPIRED: Step {idx} took {duration:.2f} ms (limit is 150ms)")
                
        except Exception as e:
            print(f"Exception at step {idx}: {e}")
            break

        # Check if process died
        if proc.poll() is not None:
            print(f"Process terminated at step {idx} with exit code {proc.returncode}")
            stderr_data = proc.stderr.read()
            print("Stderr output:")
            print(stderr_data)
            break

    # Clean up
    proc.kill()
    print("Direct test finished.")

if __name__ == '__main__':
    main()
