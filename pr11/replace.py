from collections import OrderedDict

REF_STRING = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
BELADY_STRING = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]


def fifo(refs: list[int], frames: int) -> int:
    if frames <= 0:
        return len(refs)
    memory: list[int] = []
    faults = 0
    for page in refs:
        if page not in memory:
            faults += 1
            if len(memory) >= frames:
                memory.pop(0)
            memory.append(page)
    return faults


def lru(refs: list[int], frames: int) -> int:
    if frames <= 0:
        return len(refs)
    cache: OrderedDict[int, None] = OrderedDict()
    faults = 0
    for page in refs:
        if page in cache:
            cache.move_to_end(page)
        else:
            faults += 1
            if len(cache) >= frames:
                cache.popitem(last=False)
            cache[page] = None
    return faults


def optimal(refs: list[int], frames: int) -> int:
    if frames <= 0:
        return len(refs)
    memory: list[int] = []
    faults = 0
    n = len(refs)
    for idx, page in enumerate(refs):
        if page in memory:
            continue
        faults += 1
        if len(memory) < frames:
            memory.append(page)
        else:
            victim_idx = 0
            farthest_next = -1
            for i, p in enumerate(memory):
                try:
                    next_use = refs.index(p, idx + 1)
                except ValueError:
                    victim_idx = i
                    break
                if next_use > farthest_next:
                    farthest_next = next_use
                    victim_idx = i
            memory[victim_idx] = page
    return faults


def clock(refs: list[int], frames: int) -> int:
    if frames <= 0:
        return len(refs)
    buf: list[int | None] = [None] * frames
    ref_bit: list[int] = [0] * frames
    hand = 0
    faults = 0

    for page in refs:
        if page in buf:
            idx = buf.index(page)
            ref_bit[idx] = 1
            continue

        faults += 1
        while True:
            if buf[hand] is None:
                buf[hand] = page
                ref_bit[hand] = 1
                hand = (hand + 1) % frames
                break
            if ref_bit[hand] == 0:
                buf[hand] = page
                ref_bit[hand] = 1
                hand = (hand + 1) % frames
                break
            ref_bit[hand] = 0
            hand = (hand + 1) % frames
    return faults


if __name__ == "__main__":
    print("=== Контрольная строка (Silberschatz) ===")
    for f in (3, 4):
        print(
            f"Кадров={f}: FIFO={fifo(REF_STRING, f)}, "
            f"LRU={lru(REF_STRING, f)}, Optimal={optimal(REF_STRING, f)}, Clock={clock(REF_STRING, f)}"
        )

    print("\n=== Строка для аномалии Белади ===")
    for f in (3, 4):
        print(
            f"Кадров={f}: FIFO={fifo(BELADY_STRING, f)}, "
            f"LRU={lru(BELADY_STRING, f)}, Optimal={optimal(BELADY_STRING, f)}, Clock={clock(BELADY_STRING, f)}"
        )
