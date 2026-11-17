#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/wait.h>

uint64_t get_pfn(void *vaddr) {
    int fd = open("/proc/self/pagemap", O_RDONLY);
    if (fd < 0) return 0;
    uint64_t vpn = (uintptr_t)vaddr / sysconf(_SC_PAGESIZE);
    uint64_t entry = 0;
    if (pread(fd, &entry, sizeof(entry), vpn * 8) != sizeof(entry)) {
        close(fd);
        return 0;
    }
    close(fd);
    return (entry & (1ULL << 63)) ? (entry & ((1ULL << 55) - 1)) : 0;
}

int main() {
    int fd = open("shared_test.bin", O_RDWR | O_CREAT | O_TRUNC, 0666);
    if (fd < 0 || ftruncate(fd, 4096) < 0 || write(fd, "Hello", 5) < 0) {
        perror("file init");
        return 1;
    }

    // Узнаём свободный базовый адрес для смещения в дочернем процессе
    void *hint = mmap(NULL, 4096 * 20, PROT_NONE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    munmap(hint, 4096 * 20);

    if (fork() == 0) {
        // Отображаем файл со смещением на 10 страниц от базового адреса
        void *target_addr = (char *)hint + 4096 * 10;
        char *ptr = mmap(target_addr, 4096, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
        volatile char c = ptr[0];
        (void)c;
        printf("[Child ] Virt: %p -> PFN: 0x%lx\n", ptr, get_pfn(ptr));
        exit(0);
    } else {
        char *ptr = mmap(hint, 4096, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
        volatile char c = ptr[0];
        (void)c;
        printf("[Parent] Virt: %p -> PFN: 0x%lx\n", ptr, get_pfn(ptr));
        wait(NULL);
    }
    close(fd);
    unlink("shared_test.bin");
    return 0;
}
