CC = gcc
CFLAGS = -Wall -Wextra -Werror -g -O2

all: allocator_test

allocator_test: main_test.o my_allocator.o
	$(CC) $(CFLAGS) -o allocator_test main_test.o my_allocator.o

main_test.o: main_test.c my_allocator.h
	$(CC) $(CFLAGS) -c main_test.c

my_allocator.o: my_allocator.c my_allocator.h
	$(CC) $(CFLAGS) -c my_allocator.c

valgrind: allocator_test
	valgrind --leak-check=full --show-leak-kinds=all ./allocator_test

clean:
	rm -f *.o allocator_test
