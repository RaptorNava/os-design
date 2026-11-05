#ifndef MY_ALLOCATOR_H
#define MY_ALLOCATOR_H

#include <stddef.h>

typedef enum {
    STRATEGY_FIRST_FIT,
    STRATEGY_BEST_FIT
} AllocStrategy;

void init_my_allocator(size_t pool_size, AllocStrategy strat);
void cleanup_my_allocator(void);

void* my_malloc(size_t size);
void my_free(void *ptr);
void* my_realloc(void *ptr, size_t size);
void set_strategy(AllocStrategy strat);

// Отладочные функции
void check_leaks_and_corruptions(void);
void print_allocator_stats(void);

#endif
