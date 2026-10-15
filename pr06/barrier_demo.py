import threading
import time

class Barrier:
    def __init__(self, num_threads):
        self.num_threads = num_threads
        self.count = 0
        self.mutex = threading.Lock()
        self.cv = threading.Condition(self.mutex)

    def wait(self):
        with self.cv:
            self.count += 1
            if self.count == self.num_threads:
                self.count = 0
                self.cv.notify_all()
            else:
                self.cv.wait()

def worker(tid, barrier):
    for phase in range(1, 4):
        print(f"Поток {tid} выполняет фазу {phase}")
        time.sleep(0.1)
        barrier.wait()
        print(f"Поток {tid} прошел барьер после фазы {phase}")

if __name__ == "__main__":
    b = Barrier(4)
    threads = [threading.Thread(target=worker, args=(i, b)) for i in range(4)]
    for t in threads: t.start()
    for t in threads: t.join()
    print("Все потоки завершили три фазы через барьер.")
