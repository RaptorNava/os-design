import random
import matplotlib.pyplot as plt
from replace import REF_STRING, BELADY_STRING, fifo, lru, optimal, clock


def gen_locality_refs(n: int = 500, num_pages: int = 16) -> list[int]:
    rng = random.Random(42)
    refs = []
    hot = [0, 1, 2, 3]
    for _ in range(n):
        if rng.random() < 0.8:
            refs.append(rng.choice(hot))
        else:
            refs.append(rng.randrange(num_pages))
    return refs


def gen_random_refs(n: int = 500, num_pages: int = 16) -> list[int]:
    rng = random.Random(42)
    return [rng.randrange(num_pages) for _ in range(n)]


def main():
    frame_counts = list(range(1, 9))
    algos = {
        "FIFO": fifo,
        "LRU": lru,
        "Optimal": optimal,
        "Clock": clock,
    }

    plt.figure(figsize=(8, 4.5))
    for name, fn in algos.items():
        faults_list = [fn(REF_STRING, k) for k in frame_counts]
        plt.plot(frame_counts, faults_list, marker="o", label=name)
    plt.title("Число отказов страниц vs число кадров (Silberschatz)")
    plt.xlabel("Число кадров")
    plt.ylabel("Число страничных отказов")
    plt.xticks(frame_counts)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.savefig("faults_vs_frames.png", dpi=150)
    print("График сохранён в faults_vs_frames.png")

    print("\n=== Сравнение на потоках с локальностью и случайном (frames=4) ===")
    loc_refs = gen_locality_refs()
    rnd_refs = gen_random_refs()
    for label, seq in [("Локальность", loc_refs), ("Случайный", rnd_refs)]:
        row = ", ".join(f"{name}={fn(seq, 4)}" for name, fn in algos.items())
        print(f"{label:12s}: {row}")


if __name__ == "__main__":
    main()
