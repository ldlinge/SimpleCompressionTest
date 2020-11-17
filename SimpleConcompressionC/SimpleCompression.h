#pragma once
#include <Python.h>

extern "C"
{
	__declspec(dllexport) int simple_compress(unsigned char* data_ptr, int data_size);
	__declspec(dllexport) void free_mem(unsigned char* a);
}

