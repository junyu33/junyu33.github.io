layout: post

title: 如何手动测量 Risc-V 处理器的 CPU 频率  

author: junyu33

tags: 

- linux
- assembly

categories: 

- 笔记

date: 2024-12-6 17:00:00

---

之前长文章写起来有些累，现在写一篇短的。

<!-- more -->

# background

由于我之前在给 Risc-V 开发板配跳板机环境时，在相关论坛上留下了自己的联系方式。于是今天有人找到我，他认为 ubuntu 镜像是在 CanMV-K230 的大核（1.6 GHz）中，而我之前强调是在小核（800 MHz），想让我看一看。

首先 `lscpu`，`cat /proc/cpuinfo` 肯定是用不了的。同时 `/sys/bus/cpu/devices/cpu0/cpufreq/` 也不存在，因此只能尝试手写代码衡量 CPU 频率。

# solution

一个简单的解决方式是通过 Linux 系统调用 `clock_gettime` 获取当前时间，然后中间运行一定数量级的指令来减小测量误差：

```
#define NUM_INSTRUCTIONS (1000000000)

asm volatile (
    "1:\n"
    "   nop\n"
    "   addi %[counter], %[counter], -1\n"
    "   bnez %[counter], 1b\n" 
    : 
    : [counter] "r"(NUM_INSTRUCTIONS)  
    : "memory"  
);
```

代码的含义是从 1e9 开始，先执行一个 `nop` 指令（实际上为 `addi x0, x0, 0`)，然后将计数器自减，最后判断计数器是否为零。

我们简单计算一下指令条数，`addi` 与 `bnez` 都是一个时钟周期。当然，考虑到现代 CPU 会执行分支预测与乱序执行，`bnez` 在大多数情况下会直接跳过。因此实际上这段循环在理想情况下（例如反复多次运行）会耗费两个时钟周期。

因此，这段代码，再加上循环前后的两个系统调用花费的时间，实际上会耗费略多于 2e9 个时钟周期。当然这点误差应该对于判断是 1.6GHz 还是 800 MHz 是完全可以忽略的。

最后就可以直接用 2e9 除以运行的时间，就可以获得以 GHz 为单位的结果了。

最终代码如下：

```c
#include <stdio.h>
#include <time.h>

#define NUM_INSTRUCTIONS (1 * 1000000000)

int main() {
    struct timespec start, end;
    clock_gettime(CLOCK_REALTIME, &start);

    asm volatile (
        "1:\n"
                                "               nop\n"
        "   addi %[counter], %[counter], -1\n"
        "   bnez %[counter], 1b\n"
        :
        : [counter] "r"(NUM_INSTRUCTIONS)
        : "memory"
    );

    clock_gettime(CLOCK_REALTIME, &end);

    long long start_time_ns = start.tv_sec * 1000000000 + start.tv_nsec;
    long long end_time_ns = end.tv_sec * 1000000000 + end.tv_nsec;
    long long elapsed_time_ns = end_time_ns - start_time_ns;

    printf("Elapsed time: %lld ns\n", elapsed_time_ns);
                printf("Elapsed Freq: %.3f GHz\n", 2e9 / elapsed_time_ns);

    return 0;
}
```

运行结果：

```sh
junyu33@zjy-canmv:~/tmp$ ./test
Elapsed time: 1296113478 ns
Elapsed Freq: 1.543 GHz
junyu33@zjy-canmv:~/tmp$ ./test
Elapsed time: 1297572988 ns
Elapsed Freq: 1.541 GHz
junyu33@zjy-canmv:~/tmp$ ./test
Elapsed time: 1294495232 ns
Elapsed Freq: 1.545 GHz
junyu33@zjy-canmv:~/tmp$ ./test
Elapsed time: 1294133798 ns
Elapsed Freq: 1.545 GHz
junyu33@zjy-canmv:~/tmp$ ./test
Elapsed time: 1294905847 ns
Elapsed Freq: 1.545 GHz
```

# summary

那位朋友最后也用了我的代码给他的开发板做了测试，结果是 1.598 GHz。因此，他是对的。
