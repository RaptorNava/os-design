#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <time.h>

#define ARRAY_SIZE (256 * 1024 * 1024)

double now_sec() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

int main(int argc, char **argv) {
    int stride = (argc > 1) ? atoi(argv[1]) : 4096;
    int use_huge = (argc > 2) ? atoi(argv[2]) : 0;

    char *arr = aligned_alloc(2 * 1024 * 1024, ARRAY_SIZE);
    if (use_huge) {
        madvise(arr, ARRAY_SIZE, MADV_HUGEPAGE);
    }
    memset(arr, 1, ARRAY_SIZE);

    volatile long sum = 0;
    double t0 = now_sec();
    for (int iter = 0; iter < 50; iter++) {
        for (size_t i = 0; i < ARRAY_SIZE; i += stride) {
            sum += arr[i];
        }
    }
    double t1 = now_sec();
    printf("Stride=%d, HugePages=%d -> Time: %.4f s\n", stride, use_huge, t1 - t0);
    free(arr);
    return 0;
}
