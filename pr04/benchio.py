import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def fetch_url(url_id):
    time.sleep(0.1) # Симуляция сетевой задержки (I/O bound)
    return f"Data {url_id}"

if __name__ == "__main__":
    urls = list(range(20))
    print("Запуск I/O бенчмарка...")

    # 1. Последовательно
    t0 = time.time()
    for u in urls:
        fetch_url(u)
    print(f"Sequential I/O time: {time.time() - t0:.4f}s")

    # 2. ThreadPoolExecutor (4 потока)
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(fetch_url, urls))
    print(f"ThreadPool (4) time:  {time.time() - t0:.4f}s")

    # 3. ProcessPoolExecutor (4 процесса)
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=4) as executor:
        list(executor.map(fetch_url, urls))
    print(f"ProcessPool (4) time: {time.time() - t0:.4f}s")
