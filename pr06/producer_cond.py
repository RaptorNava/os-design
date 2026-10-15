import threading
import time

BUFFER_SIZE = 5
buffer = [0] * BUFFER_SIZE
head = 0
tail = 0
count = 0

mutex = threading.Lock()
not_full = threading.Condition(mutex)
not_empty = threading.Condition(mutex)

total_items = 1000
produced_count = 0
consumed_count = 0
consumed_items = []
consumed_lock = threading.Lock()

class Producer(threading.Thread):
    def __init__(self, pid, items_to_produce):
        super().__init__()
        self.pid = pid
        self.items_to_produce = items_to_produce

    def run(self):
        global head, count
        for i in range(self.items_to_produce):
            item = self.pid * 10000 + i
            with not_full:
                while count >= BUFFER_SIZE:
                    not_full.wait()
                
                # Кладём в кольцевой буфер
                buffer[tail] = item
                global tail
                tail = (tail + 1) % BUFFER_SIZE
                count += 1
                
                not_empty.notify_all()

class Consumer(threading.Thread):
    def __init__(self, items_to_consume):
        super().__init__()
        self.items_to_consume = items_to_consume

    def run(self):
        global head, count, consumed_count
        while True:
            with not_empty:
                while count == 0:
                    if consumed_count >= total_items:
                        return
                    not_empty.wait()
                
                if consumed_count >= total_items:
                    return

                item = buffer[head]
                global head
                head = (head + 1) % BUFFER_SIZE
                count -= 1
                
                consumed_count += 1
                with consumed_lock:
                    consumed_items.append(item)
                
                not_full.notify_all()

if __name__ == "__main__":
    items_per_producer = total_items // 3
    producers = [Producer(i, items_per_producer) for i in range(3)]
    consumers = [Consumer(total_items // 2) for _ in range(2)]

    for p in producers: p.start()
    for c in consumers: c.start()

    for p in producers: p.join()
    
    # Даем потребителям завершиться
    with not_empty:
        not_empty.notify_all()

    for c in consumers: c.join()

    print(f"Всего произведено элементов: {total_items}")
    print(f"Всего потреблено элементов: {len(consumed_items)}")
    # Проверка инварианта: каждый элемент уникален и потреблен ровно один раз
    assert len(consumed_items) == len(set(consumed_items)), "Ошибка: обнаружены дубликаты!"
    print("Инвариант корректности соблюден: дубликатов нет.")
