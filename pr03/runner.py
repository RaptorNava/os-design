import os
import time

commands = [["sleep", "1"], ["ls", "-l"], ["echo", "Hello from child"]]
pids = []

start_time = time.time()
for cmd in commands:
    pid = os.fork()
    if pid == 0:
        os.execvp(cmd[0], cmd)
    else:
        pids.append(pid)

for pid in pids:
    _, status = os.waitpid(pid, 0)
    print(f"Процесс {pid} завершился со статусом {status}")

print(f"Все заняло: {time.time() - start_time:.2f} сек.")
