import math

# Попытка импорта matplotlib для графиков (опционально)
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

MEMORY_SIZE = 1024

class MemoryManager:
    def __init__(self, size=MEMORY_SIZE, enable_coalescing=False):
        self.total_size = size
        self.enable_coalescing = enable_coalescing
        self.blocks = [{'pid': None, 'start': 0, 'size': size}]
        self.failures = 0
        self.internal_frag_sum = 0
        self.external_frag_sum = 0
        self.alloc_count = 0

    def print_map(self, title=""):
        res = []
        for b in self.blocks:
            tag = b['pid'] if b['pid'] else "Free"
            res.append(f"[{tag}: {b['start']}-{b['start']+b['size']-1}]")
        print(f"{title:25s} -> " + " ".join(res))

    def _coalesce(self):
        if not self.enable_coalescing:
            return
        new_blocks = []
        for b in self.blocks:
            if new_blocks and new_blocks[-1]['pid'] is None and b['pid'] is None:
                new_blocks[-1]['size'] += b['size']
            else:
                new_blocks.append(dict(b))
        self.blocks = new_blocks

    def alloc(self, pid, size, strategy='first_fit'):
        self.alloc_count += 1
        target_idx = -1

        candidates = []
        for idx, b in enumerate(self.blocks):
            if b['pid'] is None and b['size'] >= size:
                candidates.append((idx, b))

        if not candidates:
            self.failures += 1
            self._record_frag(0)
            return False

        if strategy == 'first_fit':
            target_idx = candidates[0][0]
        elif strategy == 'best_fit':
            candidates.sort(key=lambda x: x[1]['size'])
            target_idx = candidates[0][0]
        elif strategy == 'worst_fit':
            candidates.sort(key=lambda x: x[1]['size'], reverse=True)
            target_idx = candidates[0][0]

        b = self.blocks[target_idx]
        if b['size'] == size:
            b['pid'] = pid
        else:
            new_allocated = {'pid': pid, 'start': b['start'], 'size': size}
            new_free = {'pid': None, 'start': b['start'] + size, 'size': b['size'] - size}
            self.blocks.pop(target_idx)
            self.blocks.insert(target_idx, new_free)
            self.blocks.insert(target_idx, new_allocated)

        self._record_frag(0)
        return True

    def free(self, pid):
        for b in self.blocks:
            if b['pid'] == pid:
                b['pid'] = None
        self._coalesce()

    def _record_frag(self, internal_frag):
        free_blocks = [b['size'] for b in self.blocks if b['pid'] is None]
        total_free = sum(free_blocks)
        max_free = max(free_blocks) if free_blocks else 0
        ext_frag = total_free - max_free
        self.external_frag_sum += ext_frag
        self.internal_frag_sum += internal_frag

    def get_external_frag(self):
        free_blocks = [b['size'] for b in self.blocks if b['pid'] is None]
        total_free = sum(free_blocks)
        max_free = max(free_blocks) if free_blocks else 0
        return total_free, max_free


class BuddySystem:
    def __init__(self, size=MEMORY_SIZE):
        self.total_size = size
        self.tree = [{'pid': None, 'start': 0, 'size': size}]
        self.failures = 0
        self.internal_frag_sum = 0
        self.external_frag_sum = 0
        self.alloc_count = 0

    def alloc(self, pid, size):
        self.alloc_count += 1
        req_size = 1 << (size - 1).bit_length()
        if req_size < 1:
            req_size = 1

        best_idx = -1
        best_size = float('inf')
        for i, b in enumerate(self.tree):
            if b['pid'] is None and b['size'] >= req_size and b['size'] < best_size:
                best_idx = i
                best_size = b['size']

        if best_idx == -1:
            self.failures += 1
            self._record_frag(0)
            return False

        while self.tree[best_idx]['size'] > req_size:
            b = self.tree.pop(best_idx)
            half = b['size'] // 2
            b1 = {'pid': None, 'start': b['start'], 'size': half}
            b2 = {'pid': None, 'start': b['start'] + half, 'size': half}
            self.tree.insert(best_idx, b2)
            self.tree.insert(best_idx, b1)

        self.tree[best_idx]['pid'] = pid
        internal_frag = req_size - size
        self._record_frag(internal_frag)
        return True

    def free(self, pid):
        for b in self.tree:
            if b['pid'] == pid:
                b['pid'] = None
        self._merge_buddies()

    def _merge_buddies(self):
        merged = True
        while merged:
            merged = False
            i = 0
            while i < len(self.tree) - 1:
                b1 = self.tree[i]
                b2 = self.tree[i+1]
                if (b1['pid'] is None and b2['pid'] is None and 
                    b1['size'] == b2['size'] and 
                    (b1['start'] % (b1['size'] * 2) == 0)):
                    new_b = {'pid': None, 'start': b1['start'], 'size': b1['size'] * 2}
                    self.tree.pop(i+1)
                    self.tree.pop(i)
                    self.tree.insert(i, new_b)
                    merged = True
                    break
                i += 1

    def _record_frag(self, internal_frag):
        free_blocks = [b['size'] for b in self.tree if b['pid'] is None]
        total_free = sum(free_blocks)
        max_free = max(free_blocks) if free_blocks else 0
        ext_frag = total_free - max_free
        self.external_frag_sum += ext_frag
        self.internal_frag_sum += internal_frag


def run_ops(filename):
    ops = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if not parts:
                continue
            if parts[0] == 'alloc':
                ops.append(('alloc', parts[1], int(parts[2])))
            elif parts[0] == 'free':
                ops.append(('free', parts[1]))
    return ops

# --- ВАРИАНТ А ---
print("=== ВАРИАНТ А: Пошаговый First Fit на ops1.txt ==[cite: 1] ===")
ops1 = run_ops('ops1.txt')
mm_a = MemoryManager(1024, enable_coalescing=False)
for op in ops1:
    if op[0] == 'alloc':
        mm_a.alloc(op[1], op[2], 'first_fit')
    else:
        mm_a.free(op[1])
    mm_a.print_map(f"{op[0]} {op[1]}")

print("\n=== ВАРИАНТ А: Сравнение 3 стратегий на ops1.txt (без coalescing) ==[cite: 1] ===")
print(f"{'Стратегия':<12} | {'Свободно (всего)':<16} | {'Макс. свободный блок':<20} | {'Внешняя фрагм.':<18}")
print("-" * 75)
for st in ['first_fit', 'best_fit', 'worst_fit']:
    mm = MemoryManager(1024, enable_coalescing=False)
    for op in ops1:
        if op[0] == 'alloc':
            mm.alloc(op[1], op[2], st)
        else:
            mm.free(op[1])
    tf, mf = mm.get_external_frag()
    print(f"{st:<12} | {tf:<16} | {mf:<20} | {tf - mf:<18}")

# --- ВАРИАНТ B ---
print("\n=== ВАРИАНТ B: Сравнение подходов на ops2.txt ==[cite: 2] ===")
ops2 = run_ops('ops2.txt')

results = {}
strategies = ['first_fit', 'best_fit', 'worst_fit']

for st in strategies:
    mm = MemoryManager(1024, enable_coalescing=True)
    for op in ops2:
        if op[0] == 'alloc':
            mm.alloc(op[1], op[2], st)
        else:
            mm.free(op[1])
    avg_ext = mm.external_frag_sum / mm.alloc_count
    avg_int = mm.internal_frag_sum / mm.alloc_count
    results[st] = (mm.failures, avg_ext, avg_int)

buddy = BuddySystem(1024)
for op in ops2:
    if op[0] == 'alloc':
        buddy.alloc(op[1], op[2])
    else:
        buddy.free(op[1])
avg_ext_b = buddy.external_frag_sum / buddy.alloc_count
avg_int_b = buddy.internal_frag_sum / buddy.alloc_count
results['buddy'] = (buddy.failures, avg_ext_b, avg_int_b)

print(f"{'Подход':<12} | {'Отказы (Failures)':<18} | {'Ср. Внешняя Фрагм.':<20} | {'Ср. Внутренняя Фрагм.':<22}")
print("-" * 80)
for name, res in results.items():
    print(f"{name:<12} | {res[0]:<18} | {res[1]:<20.2f} | {res[2]:<22.2f}")

# Опциональное построение графика, если установлена библиотека matplotlib
if HAS_MATPLOTLIB:
    names = list(results.keys())
    failures = [results[k][0] for k in names]
    ext_frag = [results[k][1] for k in names]
    int_frag = [results[k][2] for k in names]

    plt.figure(figsize=(10, 5))

    plt.subplot(1, 2, 1)
    plt.bar(names, failures, color=['#800020', '#a83244', '#d9534f', '#2b2b2b'])
    plt.title("Число отказов (Failures) на ops2")
    plt.ylabel("Количество отказов")

    plt.subplot(1, 2, 2)
    plt.bar(names, ext_frag, label="Внешняя фрагментация", color='#800020', alpha=0.8)
    plt.bar(names, int_frag, bottom=ext_frag, label="Внутренняя фрагментация", color='#4a4a4a')
    plt.title("Средняя фрагментация на ops2")
    plt.ylabel("Размер в единицах")
    plt.legend()

    plt.tight_layout()
    plt.savefig("fragmentation_comparison.png")
    print("\n[INFO] Библиотека matplotlib обнаружена: график успешно сохранен в 'fragmentation_comparison.png'")
else:
    print("\n[INFO] Библиотека matplotlib не установлена: симуляция выполнена полностью в текстовом режиме (без генерации графика).")
