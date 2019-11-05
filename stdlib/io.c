#include <stdio.h>
#include <stdint.h>

void print_i64(int64_t value)
{
    printf("%ld\n", value);
}

void print_i32(int32_t value)
{
    printf("%d\n", value);
}

void print_i16(int16_t value)
{
    printf("%d\n", value);
}

void print_i8(int8_t value)
{
    printf("%hhd\n", value);
}

void print_u64(uint64_t value)
{
    printf("%ld\n", value);
}

void print_u32(uint32_t value)
{
    printf("%u\n", value);
}

void print_u16(uint16_t value)
{
    printf("%hu\n", value);
}

void print_u8(uint8_t value)
{
    printf("%hhu\n", value);
}
