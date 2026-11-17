from collections import OrderedDict
import random
import matplotlib.pyplot as plt

PAGE_SIZE = 1024
MEM_TIME = 100.0  # нс
TLB_TIME = 10.0   # нс

class LRUTLB:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.hits = 0
        self.misses = 0

    def access(self, page: int, page_table: dict[int, int]) -> tuple[bool, int | None]:
        if self.capacity > 0 and page in self.cache:
            self.hits += 1
            self.cache.move_to_end(page)
            return True, self.cache[page]
        
        self.misses += 1
        frame = page_table.get(page)
        if frame is not None and self.capacity > 0:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
            self.cache[page] = frame
        return False, frame

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

def calc_eat(hit_rate: float, mem_time: float = MEM_TIME, tlb_time: float = TLB_TIME) -> float:
    return hit_rate * (tlb_time + mem_time) + (1 - hit_rate) * (tlb_time + 2 * mem_time)

def simulate_two_level_pt(addr: int) -> int:
    p1 = (addr >> 12) & 0b11
    p2 = (addr >> 10) & 0b11
    offset = addr & 0x3FF
    
    page_dir = {0: {0: 5, 1: 2, 2: 7, 3: 0}}
    
    mem_accesses = 0
    mem_accesses += 1  # Каталог страниц
    second_level = page_dir.get(p1)
    if second_level is None or p2 not in second_level:
        print(f"[2-Level PT] Адрес {addr}: Page Fault")
        return mem_accesses
    
    mem_accesses += 1  # Таблица второго уровня
    frame = second_level[p2]
    
    mem_accesses += 1  # Доступ к данным
    phys_addr = frame * PAGE_SIZE + offset
    print(f"[2-Level PT] Адрес {addr} -> p1={p1}, p2={p2}, off={offset} -> физ.{phys_addr} (Обращений к RAM: {mem_accesses})")
    return mem_accesses

if __name__ == "__main__":
    full_pt = {i: (i * 3 + 5) % 32 for i in range(16)}
    
    print("=== Эффективное время доступа (EAT) ===")
    for hr in [0.0, 0.5, 0.8, 0.95, 0.99]:
        print(f"Hit Rate = {hr*100:5.1f}% -> EAT = {calc_eat(hr):6.2f} нс")

    random.seed(42)
    hot_pages = [1, 2, 3]
    refs_locality = []
    for _ in range(5000):
        page = random.choice(hot_pages) if random.random() < 0.8 else random.randint(0, 15)
        refs_locality.append(page * PAGE_SIZE + random.randint(0, PAGE_SIZE - 1))

    tlb_4 = LRUTLB(capacity=4)
    for addr in refs_locality:
        tlb_4.access(addr // PAGE_SIZE, full_pt)
    print(f"\nНа потоке с локальностью (K=4): Hit Rate = {tlb_4.hit_rate*100:.2f}%, EAT = {calc_eat(tlb_4.hit_rate):.2f} нс")

    sizes = list(range(1, 17))
    hit_rates = []
    for k in sizes:
        tlb = LRUTLB(capacity=k)
        for addr in refs_locality:
            tlb.access(addr // PAGE_SIZE, full_pt)
        hit_rates.append(tlb.hit_rate * 100)

    plt.figure(figsize=(8, 4.5))
    plt.plot(sizes, hit_rates, marker="o", linewidth=2)
    plt.title("Зависимость Hit Rate от размера TLB (политика LRU)")
    plt.xlabel("Количество записей в TLB (K)")
    plt.ylabel("Доля попаданий, %")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.xticks(sizes)
    plt.savefig("tlb_hit_rate.png", dpi=150)
    print("График сохранён в tlb_hit_rate.png")

    print("\n=== Двухуровневая таблица страниц ===")
    simulate_two_level_pt(1200)
