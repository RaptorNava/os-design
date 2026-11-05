#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "my_allocator.h"

#define POOL_SIZE (1024 * 1024 * 32) // 32 МБ

void scenario_small_allocations(void) {
    printf("Сценарий 1: Много мелких выделений (10000 объектов по 16-64 байт)\n");
    void *ptrs[10000];
    clock_t start = clock();

    for (int i = 0; i < 10000; i++) {
        ptrs[i] = my_malloc(16 + (i % 48));
    }
    for (int i = 0; i < 10000; i++) {
        my_free(ptrs[i]);
    }

    clock_t end = clock();
    printf("  Время выполнения: %.4f сек\n", (double)(end - start) / CLOCKS_PER_SEC);
}

void scenario_alternating_alloc_free(void) {
    printf("Сценарий 2: Чередование alloc/free (фрагментационный стресс-тест)\n");
    void *ptrs[2000];
    clock_t start = clock();

    for (int i = 0; i < 2000; i++) {
        ptrs[i] = my_malloc(128);
    }
    for (int i = 0; i < 2000; i += 2) { // Освобождаем каждый второй
        my_free(ptrs[i]);
    }
    for (int i = 0; i < 1000; i++) {
        my_malloc(64); // Заполняем образовавшиеся дыры
    }
    for (int i = 1; i < 2000; i += 2) {
        my_free(ptrs[i]);
    }

    clock_t end = clock();
    printf("  Время выполнения: %.4f сек\n", (double)(end - start) / CLOCKS_PER_SEC);
}

int main(void) {
    printf("=== СТАРТ ТЕСТИРОВАНИЯ КАСТОМНОГО АЛЛОКАТОРА (mmap) ===\n");

    printf("\n--- Стратегия: FIRST FIT ---\n");
    init_my_allocator(POOL_SIZE, STRATEGY_FIRST_FIT);
    scenario_small_allocations();
    scenario_alternating_alloc_free();
    check_leaks_and_corruptions();
    cleanup_my_allocator();

    printf("\n--- Стратегия: BEST FIT ---\n");
    init_my_allocator(POOL_SIZE, STRATEGY_BEST_FIT);
    scenario_small_allocations();
    scenario_alternating_alloc_free();
    check_leaks_and_corruptions();
    cleanup_my_allocator();

    return 0;
}
