import os

print(f"{'PID':<6} {'PPID':<6} {'STATUS':<8} {'COMMAND'}")
for pid in sorted([int(p) for p in os.listdir('/proc') if p.isdigit()]):
    try:
        with open(f"/proc/{pid}/stat", "r") as f:
            data = f.read().split()
            print(f"{data[0]:<6} {data[3]:<6} {data[2]:<8} {data[1]}")
    except Exception:
        pass
