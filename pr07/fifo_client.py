import sys

REQ_FIFO = "/tmp/req_fifo"
RESP_FIFO = "/tmp/resp_fifo"

expr = sys.argv[1] if len(sys.argv) > 1 else "2+2*2"

with open(REQ_FIFO, "w") as wf:
    wf.write(expr + "\n")

with open(RESP_FIFO, "r") as rf:
    ans = rf.readline().strip()
    print(f"Результат от сервера: {ans}")
