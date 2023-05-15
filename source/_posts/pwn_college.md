layout: post
title: （置顶）pwncollege部分通关记录
author: junyu33
mathjax: true
tags: 

- pwn

categories:

  - ctf

date: 2032-7-3 18:00:00

---

指 https://dojo.pwn.college/challenges 

按照网站要求，这里只提供思路和前两题的exploit。

<!-- more -->

# heap

## babyheap1.0~2.1——uaf

```python
def exploit():
   malloc(flag_size)
   free()
   read_flag()
   puts()
```

## babyheap3.0~3.1——uaf2.0

注意tcache是LIFO结构

## babyheap4.0&4.1——tcache double free

第一次独立写出堆题，虽然是最简单的那种`tcache double free`。

## babyheap5.0&5.1——unsorted bin attack

libc 2.23->libc 2.31

通过耗尽所有的tcache来触发small bin和unsorted bin，进而修改chunk。

## babyheap6.0&6.1——tcache poisoning

简单的tcache poisoning

https://wargames.ret2.systems/level/how2heap_tcache_poisoning_2.31

## babyheap7.0&7.1——tcache poisoning2.0

由于flag不会变化，secret后半部分，只需将sec_addr+=8，重新运行即可。

## babyheap8.0&8.1——brute force

通过先前的方法可以泄露出secret的后12位，前4位可以通过暴力枚举实现。

脚本跑了一节课才跑出来。

## babyheap9.0——tcache double free

由于允许uaf，第一次free过后将next指针置0，即可double free。

此时如果将next改成`0x42b321`就可在给出的堆信息中看到key。

## babyheap9.1——tcache double free | perthread corruption

接着上一关的步骤，接着malloc两次，虽然题目禁止你读取key附近的指针，但malloc操作还是进行了。

由于`tcache`的链表特性，`addr+8`处会被清零。再进行一次这样的操作后，可以输入16个`\0`通过验证。

通过修改地址到perthread struct读取在链表头的8字节key理论上可行，就没试了。

## babyheap10.0&10.1——heap on stack

给出了栈地址与elf地址，因此直接把堆放到栈上，修改retn地址即可。

## babyheap11.0&11.1——free_hook+arbitary read

由于不知道elf地址和栈地址，首先我覆盖`free_hook`（注意写free_hook的时候size位最好是`\x7f`）成为`system_plt`拿到了shell，但是并没有权限。

然后发现执行echo函数后会多开辟一个堆空间，里面有elf与stack相关的地址，而且echo函数没有限制偏移大小，因此可以拿到这些地址。

由于我已经可以写`free_hook`，直接将`free_hook`覆盖成`win`即可。

## babyheap12.0&12.1——modify size

由于`tcache`的机制，修改栈上堆的`size`即可绕过合法性检测。

## babyheap13.0——tcache double free

 类似于babyheap9.1的做法，分配到`sec`附近，然后输入一堆`\0`覆盖`key`。

## babyheap13.1——modify size

由于sec与堆的偏移不超过一个字节，修改栈上堆的`size`之后，使用`malloc`分配一个稍微大点的堆填充数据即可。

## babyheap14.0&14.1——modify size+leak elf&canary

在level13的基础上，用`echo`泄露`elf`地址与`canary`地址，然后在堆上进行栈溢出。

对于14.1，注意`\x09`不可输入，建议换一个靠后的地址。

## babyheap15.0&15.1——leak elf&stack+unlink

这个题有点tricky，我把elf、stack、libc、heap泄露完了才发现uaf已经没了。

任意写的方式除了double free就是unlink了，我懒得去想多么巧妙的堆风水，干脆直接unlink结束战斗。

> 以下的程序的libc从2.31升级到2.35.
>
> glibc 2.35与2.31有以下不同之处：
>
> - safe-linking——实际地址为加密值本身与前一项右移12位后异或的值（2.32）。
> - malloc对齐检查——地址必须与0x10对齐（2.33）。
> - 删除了`__malloc_hook`,`__free_hook`等一系列钩子（2.34）。

## babyheap16.0——tcache double free+safe-linking

逻辑和level 9相同，只需在修改next指针时做一次异或操作即可。

## babyheap16.1——tcache perthread corruption+safe-linking

由于进行了对齐检测，没有办法对addr处清零。这里只能使用tcache perthread corruption，刚好把chunk分配到key的位置进行读取。

另外读取的值也要异或一下才是最终的key。

## babyheap17.0——canary leak

把堆分配到`rbp-0x10`的位置，从打印信息中获得canary，然后栈溢出即可。

## babyheap17.1——off by null+unlink

通过scanf末尾置0的特性，把`next_chunk_size`从`0x101`置为`0x100`，从而实现unlink。

之后把`ptr`指针数组一项覆盖为返回地址，把返回地址`scanf`为`win`函数。

## babyheap18.0——off by null+unlink

思路类似，unlink后直接puts读sec数组。

## babyheap18.1——fake chunk

伪造堆块，直接覆盖sec数组。

## babyheap19.0&19.1——chunk overlapping

https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/chunk-extend-overlapping/#1inusefastbinextend

## babyheap20.0&20.1——safe-linking+libc.environ+orw rop

通过unsorted bin获取libc地址，通过堆溢出获取heap地址。

分配四个chunk，第一个chunk溢出到第二个，改变size为原来3倍。通过打印泄漏key指针，对第二个chunk进行溢出，维持第三个chunk不变，修改第四个next指针（根据safe-linking特性，这样才能修改第三个chunk的next指针）为`libc.environ ^ (heap_base >> 12)`。然后两次`malloc`打印即可获得`libc.environ`.

通过`libc.environ`获取栈地址进行unlink。

由于直接拿shell读不了flag，这里使用orw rop读取。

# kernel

## babykernel1.0~6.1——basic definition

参照这篇博客：https://www.cnblogs.com/crybaby/p/14431651.html

kernel shellcode着实有点麻人。

> 注：如何查看有没有kaslr？
>
> 进入kernel后，`demsg`查看第二行最后有没有`nokaslr`

## babykernel7.0~7.1——struct&debug

需要传入一个类似于这样的结构体：

```c
struct shellcode{
    unsigned long length;
    char shellcode[0x1000];
    unsigned long* shellcode_addr;
}
```

注意以下几点：

- shellcode必须包含ret语句（ret2usr）。
- shellcode_addr可以通过动调得到，位置固定。

## babykernel8.0~8.1——shellcode in shellcode

一句话——在shellcode里写shellcode

第一次进内核来一遍`commit_creds(prepare_kernel_cred(0))`，`ret2usr`后变成root shell。再进入一次`run_cmd /bin/chmod 777 /flag`即可修改flag权限。（注意在内核态里起shell没有任何作用）

## babykernel9.0~9.1——run_cmd

直接把`printk`指针改为`run_cmd`，然后`rdi`是输入处，写入`/bin/chmod 777 /flag`即可。

## babykernel10.0——kaslr leak

注意kaslr只有在kernel重启之后才会重新随机，所以重新运行程序，原有的kernel函数地址不会变。

与userland的aslr类似，kaslr的低5位都是固定的。写入256字节使得`printk`的地址被泄露，从而找到`run_cmd`的地址。

## babykernel10.1——partial overwrite

由于该驱动不会打印自己的输入，这里采取重写`printk`的后3字节，也就是得爆破`run_cmd`的倒数第六位。

## babykernel11.0~12.1——memory scanning

程序将flag加载到内存里，然后删掉了flag文件，因此flag只能在内存里面找。

通过discord的spoiler可以得知应该从`0xffff888000000000`开始扫内存（即宏`phys_to_virt(0)`的值，也是[源码](https://elixir.bootlin.com/linux/v5.4/source/arch/x86/include/asm/page_64_types.h#L41)中`__PAGE_OFFSET_BASE_L4`一行的值），然后`dmesg`找一下flag即可。

注意以下几点：

- 如果用[这个网站](https://shell-storm.org/online/Online-Assembler-and-Disassembler/)将汇编转成字节码，务必把字节码转成汇编验证一下是否漏掉了指令。
- 为了减少输出，建议将地址的值与`pwn.coll`（或类似的64位字符串）比较一下再打印到控制台。
- python很耗费内存，可能起一遍python，flag那部分的内存就被重新分配了。所以建议把shellcode输出到文件再进行文件流输入。

# file

> 根据linux哲学，一切皆文件，所以`stdin(0), stdout(1), stderr(2)`等都是文件。

## babyfile_level1——arbitrary write to file

如果你什么也不做，断在fwrite后，FILE结构体会是这样的：

```C
pwndbg> x/30gx 0x18203b0
0x18203b0:      0x00000000fbad2c84      0x0000000001820590
0x18203c0:      0x0000000001820590      0x0000000001820590
0x18203d0:      0x0000000001820590      0x0000000001820690
0x18203e0:      0x0000000001821590      0x0000000001820590
0x18203f0:      0x0000000001821590      0x0000000000000000
0x1820400:      0x0000000000000000      0x0000000000000000
0x1820410:      0x0000000000000000      0x00007fb7069655c0
0x1820420:      0x0000000000000004      0x0000000000000000
0x1820430:      0x0000000000000000      0x0000000001820490
0x1820440:      0xffffffffffffffff      0x0000000000000000
0x1820450:      0x00000000018204a0      0x0000000000000000
0x1820460:      0x0000000000000000      0x0000000000000000
0x1820470:      0x00000000ffffffff      0x0000000000000000
0x1820480:      0x0000000000000000      0x00007fb7069614a0
0x1820490:      0x0000000000000000      0x0000000000000000
```

所以只需要修改`file+8`到`file+0x48`的值到想要写的位置即可。

其中，`0xfbad2c00`是magic number。

```python
def exploit():
   fake_file = p64(0xfbad2c00) + p64(0x4040e0)*4 + p64(0x4041e0) + p64(0x4050e0) + p64(0x4040e0) + p64(0x4050e0)
   io.send(fake_file)
```

最后`cat /tmp/babyfile.txt`

## babyfile_level2——arbitrary read from file

这次是任意读：

```c
pwndbg> x/30gx 0x6483b0
0x6483b0:       0x00000000fbad0230      0x0000000000000000
0x6483c0:       0x0000000000000000      0x0000000000648590
0x6483d0:       0x0000000000000000      0x0000000000000000
0x6483e0:       0x0000000000000000      0x0000000000648590
0x6483f0:       0x0000000000649590      0x0000000000000000
0x648400:       0x0000000000000000      0x0000000000000000
0x648410:       0x0000000000000000      0x00007fc110d2e5c0
0x648420:       0x0000000000000003      0x0000000000000000
0x648430:       0x0000000000000000      0x0000000000648490
0x648440:       0xffffffffffffffff      0x0000000000000000
0x648450:       0x00000000006484a0      0x0000000000000000
0x648460:       0x0000000000000000      0x0000000000000000
0x648470:       0x00000000ffffffff      0x0000000000000000
0x648480:       0x0000000000000000      0x00007fc110d2a4a0
0x648490:       0x0000000000000000      0x0000000000000000
```

其中，`0xfbad000`是magic number。

注意`_IO_buf_end - _IO_buf_base`的大小需要**大于**（不能等于）缓存区的大小。

```python
def exploit():
   fake_file = p64(0xfbad0000) + p64(0)*2 + p64(0x4041f8) + p64(0)*3 + p64(0x4041f8) + p64(0x4051f8)
   io.send(fake_file)
```

## babyfile_level3——fileno redirect

直接修改`_fileno`为标准输出`1`即可。

## babyfile_level4——fileno redirect

没有开PIE，重定向到输入，输入`win`地址。

## babyfile_level5——arbitrary write to file

同level1.

## babyfile_level5——arbitrary read from file

同level2.