import threading
import multiprocessing

shared_list = [0]

def thread_func():
    shared_list.append(1)

def proc_func(lst):
    lst.append(2)

if __name__ == "__main__":
    # Потоки
    t = threading.Thread(target=thread_func)
    t.start()
    t.join()
    print("После потока, shared_list:", shared_list) # Изменился в родителе!

    # Процессы (изолированная память)
    mgr_list = multiprocessing.Manager().list([0])
    p = multiprocessing.Process(target=proc_func, args=(mgr_list,))
    p.start()
    p.join()
    print("После процесса с Manager, list:", list(mgr_list))
