#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/resource.h>

static double elapsed_sec(struct timespec a, struct timespec b) {
    return (double)(b.tv_sec - a.tv_sec) + (double)(b.tv_nsec - a.tv_nsec) * 1e-9;
}

static void print_stat_faults(const char *tag) {
    FILE *f = fopen("/proc/self/stat", "r");
    if (!f) return;
    int pid;
    char comm[256], state;
    unsigned long minflt = 0, majflt = 0;
    /* Поля в /proc/self/stat: 1=pid, 2=comm, 3=state, ..., 10=minflt, 12=majflt */
    if (fscanf(f, "%d %255s %c", &pid, comm, &state) == 3) {
        for (int i = 4; i <= 12; i++) {
            unsigned long val = 0;
            if (fscanf(f, " %lu", &val) != 1) break;
            if (i == 10) minflt = val;
            if (i == 12) majflt = val;
        }
    }
    fclose(f);

    struct rusage ru;
    getrusage(RUSAGE_SELF, &ru);
    printf("[%s] getrusage: minflt=%ld, majflt=%ld | /proc/self/stat: minflt=%lu, majflt=%lu\n",
           tag, ru.ru_minflt, ru.ru_majflt, minflt, majflt);
}

int main(int argc, char **argv) {
    size_t mb = (argc > 1) ? (size_t)atol(argv[1]) : 256;
    int mode = (argc > 2) ? atoi(argv[2]) : 0; /* 0 = последовательно, 1 = прыжки по страницам */
    size_t bytes = mb * 1024UL * 1024UL;
    size_t page_sz = (size_t)sysconf(_SC_PAGESIZE);

    print_stat_faults("Старт");
    char *buf = malloc(bytes);
    if (!buf) {
        perror("malloc");
        return 1;
    }

    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);

    volatile unsigned char sink = 0;
    size_t n_pages = bytes / page_sz;
    for (int pass = 0; pass < 3; pass++) {
        if (mode == 0) {
            for (size_t i = 0; i < bytes; i += page_sz) {
                buf[i] = (unsigned char)(pass + 1);
                sink ^= buf[i];
            }
        } else {
            /* Большой шаг по страницам для снижения локальности рабочего множества */
            size_t step = (n_pages > 17) ? 17 : 1;
            for (size_t k = 0; k < n_pages; k++) {
                size_t idx = ((k * step) % n_pages) * page_sz;
                buf[idx] = (unsigned char)(pass + 1);
                sink ^= buf[idx];
            }
        }
    }

    clock_gettime(CLOCK_MONOTONIC, &t1);
    printf("Буфер: %zu МБ, режим: %d, время: %.4f с, sink=%u\n", mb, mode, elapsed_sec(t0, t1), sink);
    print_stat_faults("После обхода");

    free(buf);
    return 0;
}
