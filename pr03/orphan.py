import os
import time

pid = os.fork()
if pid == 0:
    print(f"Ребенок-сирота запущен, ППИД изначально: {os.getppid()}")
    time.sleep(5)
    print(f"Новый ППИД ребенка (после усыновления): {os.getppid()}")
else:
    print(f"Родитель завершается сразу, PID: {os.getpid()}")
    exit(0)
