/*
    Small Test program that shows a code reuse style attack using the Nvidia CUDA driver code that is loaded into every CUDA process.
    The buffer is filled with input from stdin, only stopping the read when \r\n\r\n is reached, thus allowing for buffer overflows.
    When using buf.bin, there is a jump to a gadget which overwriters (among others) R4, the register used for the return value of res.
    Afterwards normal execution is resumed but this now uses the wrong return value (0xdeadbeef).
*/

#include <stdio.h>
#include <stdlib.h>
#include <cstdint>

using namespace std;

__device__ __noinline__ void target_function(uint32_t* someIntArr, uint32_t index) {
    printf("Target at %p reached!\n", &target_function);
}

// function where we attempt to overwrite the return address
__device__ __noinline__ u_int32_t calling_function(uint32_t* input) {
    // Allocate a buffer which we will overflow to overwrite the return address
    u_int32_t buf[4000];

    if(input[0] == 0xdaedbeef) {
        printf("Recursion\n");
        return calling_function(&input[1]);
    }
    
    printf("target function at %p\n", &target_function);

    // Copy the buffer over from the input until we reach a \r\n\r\n
    int i = 0;
    while(input[i] != 0x0a0d0a0d) {
        printf("In loop: %d\n", i);
        uint32_t valOrig = buf[i];
        uint32_t valNew = input[i];
        printf("%d: %#08x => %#08x\n", i, valOrig, valNew);
        i++;
    }
    printf("Out of loop\n");

    u_int32_t res = 0;
    for(int i = 0; i < 400; i++) {
        printf("buf[%d]: %#08x\n", i, buf[i]);
        res += buf[i];
    }
    res += 69;
    return res; 
}

// Kernel that calls a function who's return address is written to the stack
__global__ __noinline__ void kernel_calling_function(uint32_t* input) {
    uint64_t someLocalBuffer[128]; 
    u_int32_t res = calling_function(input);
    input[0] = res;
    someLocalBuffer[0] = res;
    
    printf("res: %lu (%#08x), %p, %p\n", someLocalBuffer[0], (uint32_t) someLocalBuffer[0], input, &kernel_calling_function);
}

int main(int argc, char **argv) {
    uint32_t* buf = (u_int32_t *)malloc(8000 * sizeof(u_int32_t));
    for(int i = 0; i < 8000; i++) {
        buf[i] = 0;
    }

    char* buf_char = (char*)buf;

    // Read the buffer from stdin
    int i = 0;
    char c;
    do {
        scanf("%c", &c);
        buf_char[i] = c;
        i++;
    } while(i < 3 || buf[(i/4) - 1] != 0x0a0d0a0d);
    printf("Read %d bytes\n", i);

    uint32_t* d_buf;
    cudaMalloc(&d_buf, 8000 * sizeof(u_int32_t));
    cudaMemcpy(d_buf, buf, 8000 * sizeof(u_int32_t), cudaMemcpyHostToDevice);

    printf("Main started\n");
	kernel_calling_function<<<1, 1>>>(d_buf);
    auto err = cudaDeviceSynchronize();

    // Copy back the buffer
    cudaMemcpy(buf, d_buf, 8000 * sizeof(u_int32_t), cudaMemcpyDeviceToHost);
    printf("Result: %#08x\n", buf[0]);

    printf("Error: %d\n", err);
    printf("Error: %s\n", cudaGetErrorName(err));
    printf("Error: %s\n", cudaGetErrorString(err));
    printf("Main finished\n");
	return 0;
}