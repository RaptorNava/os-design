import time
import multiprocessing
from multiprocessing import shared_memory
import numpy as np

def pipe_worker(conn, data):
    conn.send(data)
    conn.close()

def shm_worker(shm_name, shape, dtype):
    existing_shm = shared_memory.SharedMemory(name=shm_name)
    arr = np.ndarray(shape, dtype=dtype, buffer=existing_shm.buf)
    _ = np.sum(arr)
    existing_shm.close()

if __name__ == "__main__":
    size = 10**7
    data = np.arange(size, dtype=np.int64)

    # 1. Pipe benchmark
    print("Замер передачи через Pipe...")
    parent_conn, child_conn = multiprocessing.Pipe()
    t0 = time.time()
    p = multiprocessing.Process(target=pipe_worker, args=(child_conn, data))
    p.start()
    _ = parent_conn.recv()
    p.join()
    t_pipe = time.time() - t0
    print(f"Pipe время: {t_pipe:.4f}s")

    # 2. Shared Memory benchmark
    print("Замер передачи через Shared Memory...")
    shm = shared_memory.SharedMemory(create=True, size=data.nbytes)
    shm_arr = np.ndarray(data.shape, dtype=data.dtype, buffer=shm.buf)
    shm_arr[:] = data[:]

    t0 = time.time()
    p = multiprocessing.Process(target=shm_worker, args=(shm.name, data.shape, data.dtype))
    p.start()
    p.join()
    t_shm = time.time() - t0
    print(f"Shared Memory время: {t_shm:.4f}s")

    shm.close()
    shm.unlink()
