#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>

uint64_t virt_to_phys(void *vaddr) {
    int fd = open("/proc/self/pagemap", O_RDONLY);
    if (fd < 0) {
        perror("open pagemap (требуются права root)");
        return 0;
    }

    long page_size = sysconf(_SC_PAGESIZE);
    uint64_t vaddr_u = (uint64_t)(uintptr_t)vaddr;
    uint64_t vpn = vaddr_u / page_size;
    uint64_t offset = vpn * sizeof(uint64_t);

    uint64_t entry = 0;
    if (pread(fd, &entry, sizeof(entry), offset) != sizeof(entry)) {
        perror("pread");
        close(fd);
        return 0;
    }
    close(fd);

    if (!(entry & (1ULL << 63))) {
        printf("Страница не в физической памяти!\n");
        return 0;
    }

    uint64_t pfn = entry & ((1ULL << 55) - 1);
    return (pfn * page_size) + (vaddr_u % page_size);
}

int main() {
    int target_var = 42;
    uint64_t paddr = virt_to_phys(&target_var);

    printf("PID: %d\n", getpid());
    printf("Виртуальный адрес: %p\n", (void*)&target_var);
    printf("Физический адрес:  0x%lx (PFN: 0x%lx)\n", paddr, paddr / sysconf(_SC_PAGESIZE));
    return 0;
}
