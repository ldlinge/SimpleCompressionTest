#include "pch.h"
#include <stdio.h>
#include "SimpleCompression.h"
#include <Python.h>

int simple_compress(unsigned char* data_ptr, int data_size)
{
    int src_idx = 0;
    int dst_idx = 0;
    unsigned char next_byte;

    while (src_idx < (data_size - 1))
    {
        next_byte = data_ptr[src_idx + 1];
        if (data_ptr[src_idx] == next_byte)
        {
            data_ptr[dst_idx] = 0x81;
            while ((data_ptr[++src_idx] == next_byte) && (src_idx < data_size))
            {
                data_ptr[dst_idx]++;
            }
            data_ptr[++dst_idx] = next_byte;
            dst_idx++;
        }
        else
        {
            data_ptr[dst_idx++] = data_ptr[src_idx++];
        }
    }

    if (src_idx < data_size)
    {
        data_ptr[dst_idx++] = data_ptr[src_idx];
    }

    return dst_idx;
}