#include "my_allocator.h"
#include <sys/mman.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define CANARY_MAGIC 0xDEADBEEF

typedef struct BlockHeader {
    size_t size;               // Размер полезных данных
    int is_free;               // 1 - свободен, 0 - занят
    struct BlockHeader *next;
    struct BlockHeader *prev;
    uint32_t canary;           // Защита от переполнения буфера
} BlockHeader;

static void *g_pool_start = NULL;
static size_t g_pool_size = 0;
static BlockHeader *g_head = NULL;
static AllocStrategy g_strategy = STRATEGY_FIRST_FIT;

void init_my_allocator(size_t pool_size, AllocStrategy strat) {
    g_pool_size = pool_size;
    g_strategy = strat;
    g_pool_start = mmap(NULL, g_pool_size, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (g_pool_start == MAP_FAILED) {
        perror("mmap failed");
        exit(EXIT_FAILURE);
    }

    g_head = (BlockHeader*)g_pool_start;
    g_head->size = g_pool_size - sizeof(BlockHeader) - sizeof(uint32_t);
    g_head->is_free = 1;
    g_head->next = NULL;
    g_head->prev = NULL;
    g_head->canary = CANARY_MAGIC;

    // Ставим канарейку в конец свободной области
    uint32_t *tail_canary = (uint32_t*)((char*)g_head + sizeof(BlockHeader) + g_head->size);
    *tail_canary = CANARY_MAGIC;
}

void cleanup_my_allocator(void) {
    if (g_pool_start) {
        munmap(g_pool_start, g_pool_size);
        g_pool_start = NULL;
        g_head = NULL;
    }
}

void set_strategy(AllocStrategy strat) {
    g_strategy = strat;
}

static void coalesce_free_blocks(void) {
    BlockHeader *curr = g_head;
    while (curr && curr->next) {
        if (curr->is_free && curr->next->is_free) {
            curr->size += sizeof(BlockHeader) + curr->next->size + sizeof(uint32_t);
            curr->next = curr->next->next;
            if (curr->next) {
                curr->next->prev = curr;
            }
            // Обновляем заднюю канарейку
            uint32_t *tail_canary = (uint32_t*)((char*)curr + sizeof(BlockHeader) + curr->size);
            *tail_canary = CANARY_MAGIC;
        } else {
            curr = curr->next;
        }
    }
}

void* my_malloc(size_t size) {
    if (size == 0 || !g_head) return NULL;

    // Выравнивание размера по 8 байтам
    size = (size + 7) & ~7;

    BlockHeader *curr = g_head;
    BlockHeader *best_block = NULL;

    while (curr) {
        if (curr->is_free && curr->size >= size) {
            if (g_strategy == STRATEGY_FIRST_FIT) {
                best_block = curr;
                break;
            } else if (g_strategy == STRATEGY_BEST_FIT) {
                if (!best_block || curr->size < best_block->size) {
                    best_block = curr;
                }
            }
        }
        curr = curr->next;
    }

    if (!best_block) return NULL; // Память исчерпана

    // Разделение блока, если остаток достаточно велик для размещения нового заголовка
    if (best_block->size >= size + sizeof(BlockHeader) + sizeof(uint32_t) + 16) {
        size_t old_size = best_block->size;
        best_block->size = size;
        best_block->is_free = 0;

        uint32_t *tail_canary = (uint32_t*)((char*)best_block + sizeof(BlockHeader) + best_block->size);
        *tail_canary = CANARY_MAGIC;

        BlockHeader *new_block = (BlockHeader*)((char*)tail_canary + sizeof(uint32_t));
        new_block->size = old_size - size - sizeof(BlockHeader) - sizeof(uint32_t);
        new_block->is_free = 1;
        new_block->next = best_block->next;
        new_block->prev = best_block;
        new_block->canary = CANARY_MAGIC;

        uint32_t *new_tail_canary = (uint32_t*)((char*)new_block + sizeof(BlockHeader) + new_block->size);
        *new_tail_canary = CANARY_MAGIC;

        if (best_block->next) {
            best_block->next->prev = new_block;
        }
        best_block->next = new_block;
    } else {
        best_block->is_free = 0;
    }

    return (void*)((char*)best_block + sizeof(BlockHeader));
}

void my_free(void *ptr) {
    if (!ptr) return;
    BlockHeader *header = (BlockHeader*)((char*)ptr - sizeof(BlockHeader));
    
    if (header->canary != CANARY_MAGIC) {
        fprintf(stderr, "[ERROR] Memory corruption detected before block at %p!\n", ptr);
        return;
    }

    uint32_t *tail_canary = (uint32_t*)((char*)header + sizeof(BlockHeader) + header->size);
    if (*tail_canary != CANARY_MAGIC) {
        fprintf(stderr, "[ERROR] Buffer overflow (tail canary corrupted) at %p!\n", ptr);
    }

    header->is_free = 1;
    coalesce_free_blocks();
}

void* my_realloc(void *ptr, size_t size) {
    if (!ptr) return my_malloc(size);
    if (size == 0) {
        my_free(ptr);
        return NULL;
    }

    BlockHeader *header = (BlockHeader*)((char*)ptr - sizeof(BlockHeader));
    if (header->size >= size) {
        return ptr;
    }

    void *new_ptr = my_malloc(size);
    if (new_ptr) {
        memcpy(new_ptr, ptr, header->size);
        my_free(ptr);
    }
    return new_ptr;
}

void check_leaks_and_corruptions(void) {
    BlockHeader *curr = g_head;
    int leaks = 0;
    printf("\n--- Проверка утечек памяти и целостности ---\n");
    while (curr) {
        if (curr->canary != CANARY_MAGIC) {
            printf("[FAIL] Нарушение заголовка блока: %p\n", (void*)curr);
        }
        uint32_t *tail_canary = (uint32_t*)((char*)curr + sizeof(BlockHeader) + curr->size);
        if (*tail_canary != CANARY_MAGIC) {
            printf("[FAIL] Нарушение хвоста блока (Buffer Overflow): %p\n", (void*)curr);
        }
        if (!curr->is_free) {
            printf("[LEAK] Неосвобожденный блок по адресу: %p (размер: %zu байт)\n", 
                   (void*)((char*)curr + sizeof(BlockHeader)), curr->size);
            leaks++;
        }
        curr = curr->next;
    }
    if (leaks == 0) {
        printf("[OK] Утечек памяти и повреждений буфера не обнаружено.\n");
    }
}
