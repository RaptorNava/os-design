import time
from threading import Thread
from multiprocessing import Pool

def sum_chunk(arr):
    return sum(arr)

def run_bench():
    with open("numbers.txt") as f:
        nums = [int(line) for line in f]
    
    # 1. Один поток / последовательно
    t0 = time.time()
    _ = sum(nums)
    t_seq = time.time() - t0

    # 2. 4 Потока (threading)
    chunk_size = len(nums) // 4
    chunks = [nums[i*chunk_size:(i+1)*chunk_size] for i in range(4)]
    
    t0 = time.time()
    threads = []
    results = [0] * 4
    def thread_worker(idx, chunk):
        results[idx] = sum(chunk)
    for i in range(4):
        t = Thread(target=thread_worker, args=(i, chunks[i]))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    t_threads = time.time() - t0

    # 3. 4 Процесса (multiprocessing)
    t0 = time.time()
    with Pool(4) as p:
        _ = sum(p.map(sum_chunk, chunks))
    t_proc = time.time() - t0

    return t_seq, t_threads, t_proc

if __name__ == "__main__":
    print("Запуск CPU-бенчмарка (3 повтора)...")
    seqs, ths, procs = [], [], []
    for _ in range(3):
        s, t, p = run_bench()
        seqs.append(s); ths.append(t); procs.append(p)
    print(f"Sequential median: {sorted(seqs)[1]:.4f}s")
    print(f"4 Threads median:  {sorted(ths)[1]:.4f}s")
    print(f"4 Processes median:{sorted(procs)[1]:.4f}s")
