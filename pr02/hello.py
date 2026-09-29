import sys
import os

if len(sys.argv) < 2:
    print(f"Использование: python3 {sys.argv[0]} <путь_к_файлу>", file=sys.stderr)
    sys.exit(1)

filepath = sys.argv[1]

if os.path.exists(filepath):
    size = os.path.getsize(filepath)
    print(f"Размер файла '{filepath}': {size} байт")
else:
    print(f"Ошибка: Файл '{filepath}' не найден.", file=sys.stderr)
    sys.exit(1)
