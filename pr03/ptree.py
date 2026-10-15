import os

print(f"{'PID':<6} {'PPID':<6} {'STATUS':<12} {'RSS':<10} {'COMMAND'}")
for pid in sorted([int(p) for p in os.listdir('/proc') if p.isdigit()]):
    try:
        ppid, state, rss = "0", "?", "0"
        with open(f"/proc/{pid}/stat", "r") as f:
            parts = f.read().split()
            ppid = parts[3]
            state = parts[2]
        with open(f"/proc/{pid}/status", "r") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    rss = line.split()[1] + " " + line.split()[2]
        with open(f"/proc/{pid}/comm", "r") as f:
            cmd = f.read().strip()
        print(f"{pid:<6} {ppid:<6} {state:<12} {rss:<10} {cmd}")
    except Exception:
        pass
