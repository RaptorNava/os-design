#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define N 4096

static double elapsed_sec(struct timespec a, struct timespec b) {
    return (double)(b.tv_sec - a.tv_sec) + (double)(b.tv_nsec - a.tv_nsec) * 1e-9;
}

int main(void) {
    double *A = aligned_alloc(64, (size_t)N * N * sizeof(double));
    if (!A) {
        perror("aligned_alloc");
        return 1;
    }
    for (size_t i = 0; i < (size_t)N * N; i++) {
        A[i] = (double)(i % 100) * 0.01;
    }

    struct timespec t0, t1;
    volatile double sum_row = 0.0;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (int r = 0; r < N; r++) {
        for (int c = 0; c < N; c++) {
            sum_row += A[(size_t)r * N + c];
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double t_row = elapsed_sec(t0, t1);

    volatile double sum_col = 0.0;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (int c = 0; c < N; c++) {
        for (int r = 0; r < N; r++) {
            sum_col += A[(size_t)r * N + c];
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double t_col = elapsed_sec(t0, t1);

    printf("По строкам:  %.4f с (sum=%.2f)\n", t_row, sum_row);
    printf("По столбцам: %.4f с (sum=%.2f)\n", t_col, sum_col);

    free(A);
    return 0;
}
