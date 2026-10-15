import os
import resource

def get_rss():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

# Создаем большой список (около 40 МБ)
big_list = [0] * (10 ** 7)
print(f"RSS родителя до fork: {get_rss()} KB")

pid = os.fork()
if pid == 0:
    print(f"RSS ребенка сразу после fork (до изменений): {get_rss()} KB")
    # Изменяем элемент — срабатывает Copy-on-Write
    big_list[0] = 1
    print(f"RSS ребенка после изменения списка (после COW): {get_rss()} KB")
    exit(0)
else:
    os.wait()
