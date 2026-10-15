import sys
import argparse
from collections import deque

class Process:
    def __init__(self, pid, arrival, burst, priority):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        self.priority = priority
        self.start_time = -1
        self.completion_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0
        self.response_time = -1

def load_processes(filename):
    procs = []
    with open(filename) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 3:
                pid, arr, burst = parts[0], int(parts[1]), int(parts[2])
                prio = int(parts[3]) if len(parts) > 3 else 0
                procs.append(Process(pid, arr, burst, prio))
    return procs

def calculate_metrics(processes, total_time, busy_time):
    n = len(processes)
    avg_waiting = sum(p.waiting_time for p in processes) / n
    avg_turnaround = sum(p.turnaround_time for p in processes) / n
    avg_response = sum(p.response_time for p in processes) / n
    cpu_utilization = (busy_time / total_time) * 100 if total_time > 0 else 0
    return avg_waiting, avg_turnaround, avg_response, cpu_utilization

def simulate(processes, algo, quantum=3):
    # Копируем процессы для чистоты эксперимента
    procs = [Process(p.pid, p.arrival, p.burst, p.priority) for p in processes]
    n = len(procs)
    time = 0
    completed = 0
    busy_time = 0
    
    # Для отслеживания интервалов Ганта (опционально)
    current_running = None
    
    if algo == 'fcfs':
        procs.sort(key=lambda x: x.arrival)
        for p in procs:
            if time < p.arrival:
                time = p.arrival
            p.response_time = time - p.arrival
            p.start_time = time
            time += p.burst
            p.completion_time = time
            p.turnaround_time = p.completion_time - p.arrival
            p.waiting_time = p.turnaround_time - p.burst
            busy_time += p.burst
        return procs, time, busy_time

    elif algo == 'sjf':
        ready = []
        unvisited = sorted(procs, key=lambda x: x.arrival)
        while completed < n:
            while unvisited and unvisited[0].arrival <= time:
                ready.append(unvisited.pop(0))
            if not ready:
                time = unvisited[0].arrival
                continue
            # Выбираем с минимальным burst
            ready.sort(key=lambda x: (x.burst, x.arrival))
            p = ready.pop(0)
            if p.response_time == -1:
                p.response_time = time - p.arrival
            time += p.burst
            p.completion_time = time
            p.turnaround_time = p.completion_time - p.arrival
            p.waiting_time = p.turnaround_time - p.burst
            busy_time += p.burst
            completed += 1
        return procs, time, busy_time

    elif algo == 'srtf':
        unvisited = sorted(procs, key=lambda x: x.arrival)
        ready = []
        while completed < n or ready:
            while unvisited and unvisited[0].arrival <= time:
                ready.append(unvisited.pop(0))
            if not ready:
                time = unvisited[0].arrival
                continue
            # Выбираем с минимальным remaining
            ready.sort(key=lambda x: (x.remaining, x.arrival))
            p = ready.pop(0)
            if p.response_time == -1:
                p.response_time = time - p.arrival
            
            p.remaining -= 1
            time += 1
            busy_time += 1
            
            if p.remaining == 0:
                p.completion_time = time
                p.turnaround_time = p.completion_time - p.arrival
                p.waiting_time = p.turnaround_time - p.burst
                completed += 1
            else:
                ready.append(p)
        return procs, time, busy_time

    elif algo == 'priority':
        # Вытесняющее приоритетное планирование со старением (aging)
        unvisited = sorted(procs, key=lambda x: x.arrival)
        ready = []
        while completed < n or ready:
            while unvisited and unvisited[0].arrival <= time:
                ready.append(unvisited.pop(0))
            # Старение: увеличиваем приоритет (уменьшаем числовое значение) тем, кто ждет
            for p in ready:
                if p.priority > 0 and (time - p.arrival) > 5:
                    p.priority = max(0, p.priority - 1)
            
            if not ready:
                time = unvisited[0].arrival
                continue
            
            ready.sort(key=lambda x: (x.priority, x.arrival))
            p = ready.pop(0)
            if p.response_time == -1:
                p.response_time = time - p.arrival
            
            p.remaining -= 1
            time += 1
            busy_time += 1
            
            if p.remaining == 0:
                p.completion_time = time
                p.turnaround_time = p.completion_time - p.arrival
                p.waiting_time = p.turnaround_time - p.burst
                completed += 1
            else:
                ready.append(p)
        return procs, time, busy_time

    elif algo == 'rr':
        unvisited = sorted(procs, key=lambda x: x.arrival)
        ready = deque()
        while completed < n or ready or unvisited:
            while unvisited and unvisited[0].arrival <= time:
                ready.append(unvisited.pop(0))
            if not ready:
                time = unvisited[0].arrival
                continue
            
            p = ready.popleft()
            if p.response_time == -1:
                p.response_time = time - p.arrival
            
            exec_time = min(quantum, p.remaining)
            
            # Важное соглашение для RR: проверяем процессы, прибывающие ВО ВРЕМЯ выполнения кванта,
            # и ставим их В ПЕРВУЮ очередь перед вытесненным процессом.
            for _ in range(exec_time):
                p.remaining -= 1
                time += 1
                busy_time += 1
                while unvisited and unvisited[0].arrival <= time:
                    ready.append(unvisited.pop(0))
            
            if p.remaining > 0:
                ready.append(p)
            else:
                p.completion_time = time
                p.turnaround_time = p.completion_time - p.arrival
                p.waiting_time = p.turnaround_time - p.burst
                completed += 1
        return procs, time, busy_time

    else:
        raise ValueError(f"Unknown algorithm: {algo}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CPU Scheduler Simulator")
    parser.add_argument("--algo", default="fcfs", choices=["fcfs", "sjf", "srtf", "priority", "rr"])
    parser.add_argument("--quantum", type=int, default=3)
    parser.add_argument("filename")
    args = parser.parse_args()

    procs = load_processes(args.filename)
    procs_res, total_time, busy_time = simulate(procs, args.algo, args.quantum)
    avg_w, avg_t, avg_r, cpu_u = calculate_metrics(procs_res, total_time, busy_time)

    print(f"=== Алгоритм: {args.algo.upper()} (Файл: {args.filename}) ===")
    print(f"Среднее ожидание:     {avg_w:.2f}")
    print(f"Средний оборот:      {avg_t:.2f}")
    print(f"Время отклика:       {avg_r:.2f}")
    print(f"Загрузка CPU:        {cpu_u:.2f}%")
