import threading
import time

condition_met = False
mutex = threading.Lock()
cv = threading.Condition(mutex)

def bad_waiter():
    global condition_met
    with cv:
        # ОШИБКА: используется if вместо while!
        if not condition_met:
            cv.wait()
        print("bad_waiter проснулся и продолжил работу!")

def spurious_notifier():
    global condition_met
    time.sleep(0.1)
    with cv:
        condition_met = True
        cv.notify_all()

if __name__ == "__main__":
    t1 = threading.Thread(target=bad_waiter)
    t2 = threading.Thread(target=spurious_notifier)
    t1.start(); t2.start()
    t1.join(); t2.join()
    print("Демонстрация завершена. При ложном пробуждении или гонке потоков без while поток пропускает проверку условия.")
