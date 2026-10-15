import os
import time

pid = os.fork()
if pid == 0:
    print(f"Ребенок завершается, PID: {os.getpid()}")
    exit(0)
else:
    print(f"Родитель усыпил себя. Ребенок {pid} теперь зомби.")
    time.sleep(20)  # Родитель не делает wait(), ребенок висит в статусе Z
    os.wait()
