#!/bin/bash

# Функция вывода справки в stderr
usage() {
    cat << EOF >&2
Использование: $0 <каталог> <ERROR|WARN> [--top N]

Аргументы:
  <каталог>      Путь к каталогу с лог-файлами (.log)
  <ERROR|WARN>   Уровень логирования (только ERROR или WARN)
  --top N        (Опционально) Ограничить вывод N верхними модулями

Примеры:
  $0 data ERROR --top 3
  $0 /var/log/app WARN
EOF
}

LOG_DIR=""
LEVEL=""
TOP_N=""

# Разбор аргументов командной строки
while [[ $# -gt 0 ]]; do
    case "$1" in
        --top)
            if [[ -z "$2" ]]; then
                echo "Ошибка: Для флага --top не указано значение N." >&2
                usage
                exit 1
            fi
            TOP_N="$2"
            shift 2
            ;;
        *)
            if [[ -z "$LOG_DIR" ]]; then
                LOG_DIR="$1"
            elif [[ -z "$LEVEL" ]]; then
                LEVEL="$1"
            else
                echo "Ошибка: Лишний аргумент '$1'." >&2
                usage
                exit 1
            fi
            shift
            ;;
    esac
done

# 1. Проверка отсутствия обязательных аргументов
if [[ -z "$LOG_DIR" ]] || [[ -z "$LEVEL" ]]; then
    echo "Ошибка: Не указаны обязательные аргументы." >&2
    usage
    exit 1
fi

# 2. Проверка неверного уровня логирования (только ERROR или WARN)
if [[ "$LEVEL" != "ERROR" && "$LEVEL" != "WARN" ]]; then
    echo "Ошибка: Неверный уровень логирования '$LEVEL'. Допустимы только ERROR или WARN." >&2
    usage
    exit 1
fi

# 3. Проверка существования каталога
if [[ ! -d "$LOG_DIR" ]]; then
    echo "Ошибка: Каталог '$LOG_DIR' не существует." >&2
    usage
    exit 1
fi

# 4. Проверка, что N является числом (если задан --top)
if [[ -n "$TOP_N" ]]; then
    if ! [[ "$TOP_N" =~ ^[0-9]+$ ]]; then
        echo "Ошибка: Параметр --top должен быть целым положительным числом, получено '$TOP_N'." >&2
        usage
        exit 1
    fi
fi

# Поиск лог-файлов в каталоге
log_files=("$LOG_DIR"/*.log)
if [[ ! -e "${log_files[0]}" ]]; then
    echo "Ошибка: В каталоге '$LOG_DIR' не найдены файлы .log." >&2
    exit 1
fi

# Извлечение сообщений, подсчет по модулям и вывод таблицы
# Предполагаемый формат лог-записи: [2026-03-30 12:00:00] [ERROR] [auth_module] Something failed
parsed_data=$(grep -h -E "\[?$LEVEL\]?" "$LOG_DIR"/*.log 2>/dev/null | awk -v lvl="$LEVEL" '
{
    for (i = 1; i <= NF; i++) {
        if ($i ~ /^\[.*\]$/) {
            mod = $i
            gsub(/[\[\]]/, "", mod)
            if (mod != lvl) {
                counts[mod]++
                break
            }
        }
    }
}
END {
    for (m in counts) {
        print counts[m], m
    }
}' | sort -nr)

if [[ -z "$parsed_data" ]]; then
    echo "Сообщений с уровнем $LEVEL не найдено."
    exit 0
fi

# Ограничение вывода при фланге --top
if [[ -n "$TOP_N" ]]; then
    parsed_data=$(echo "$parsed_data" | head -n "$TOP_N")
fi

# Форматированный вывод таблицы
echo "$parsed_data" | awk '
BEGIN {
    printf "%-25s %s\n", "МОДУЛЬ", "ЧИСЛО СООБЩЕНИЙ"
    print "----------------------------------------"
}
{
    printf "%-25s %s\n", $2, $1
}'
