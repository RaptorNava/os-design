import os
import sys

REQ_FIFO = "/tmp/req_fifo"
RESP_FIFO = "/tmp/resp_fifo"

for f in [REQ_FIFO, RESP_FIFO]:
    if os.path.exists(f):
        os.unlink(f)
    os.mkfifo(f)

print("FIFO Server started. Waiting for requests...")
try:
    while True:
        with open(REQ_FIFO, "r") as rf:
            expr = rf.readline().strip()
            if not expr:
                continue
            print(f"Получено выражение: {expr}")
            try:
                res = str(eval(expr))
            except Exception as e:
                res = f"Error: {e}"
        
        with open(RESP_FIFO, "w") as wf:
            wf.write(res + "\n")
except KeyboardInterrupt:
    pass
finally:
    if os.path.exists(REQ_FIFO): os.unlink(REQ_FIFO)
    if os.path.exists(RESP_FIFO): os.unlink(RESP_FIFO)
    print("FIFO Server stopped and cleaned up.")
