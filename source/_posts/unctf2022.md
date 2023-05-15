layout: post 
title: unctf2022pwn wp
author: junyu33 
mathjax: true 
categories: 

  - ctf

tags:

- pwn

date: 2022-11-21 22:20:00

---

虽然pwn AK了，但pwn手还是输麻了。

运维水平很是蛋疼，以后文件别放毒盘（

<!-- more -->

# pwn

## welcomeUNCTF2022

```c
int func()
{
  char s2[11]; // [esp+Ch] [ebp-1Ch] BYREF
  char s[13]; // [esp+17h] [ebp-11h] BYREF

  strcpy(s2, "UNCTF&2022");
  puts("Welcome to UNCTF2022 Please enter the password:");
  gets(s);
  if ( !strcmp(s, s2) )
    return system("cat /flag");
  else
    return puts("wrong!!!");
}
```

简单判断，测试nc是否正常工作~~与靶机状态~~。

## 石头剪刀布

main部分

```c
int __cdecl main(int argc, const char **argv, const char **envp)
{
  char v4; // [rsp+1Fh] [rbp-1h] BYREF

  setvbuf(stdin, 0LL, 2, 0LL);
  setvbuf(stdout, 0LL, 2, 0LL);
  setvbuf(stderr, 0LL, 2, 0LL);
  srand(0xAu);
  puts("Do you know \x1B[1;36m\"rand()\"\x1B[0m ?");
  puts("In order to help you,I can tell you a secert!!!But you need to answer my question");
  puts("Will you learn about something of pwn later?(y/n)");
  __isoc99_scanf("%c", &v4);
  if ( v4 != 0x79 )
  {
    puts("lazy dog,you can't know my secret and get out!!!");
    exit(0);
  }
  puts("good boy,I trust you");
  puts("the secert is:");
  puts("I have set a seed for \x1B[1;36m\"srand()\"?\x1B[0m");
  puts("I'm so happy.Come and play games with me");
  playgame("I'm so happy.Come and play games with me");
  return 0;
}
```

游戏部分

```c
__int64 playgame()
{
  int v1; // [rsp+4h] [rbp-Ch]
  int v2; // [rsp+8h] [rbp-8h]
  int i; // [rsp+Ch] [rbp-4h]

  rules();
  for ( i = 1; i <= 100; ++i )
  {
    printf("\x1B[1;31mround[%d]\x1B[0m\n", (unsigned int)i);
    v2 = input();
    v1 = rand() % 3;
    if ( !v2 && v1 != 1 || v2 == 1 && v1 != 2 || v2 == 2 && v1 )
      gameover();
    puts("success!!!");
  }
  return backdoor();
}
```

给定了随机种子，只需在Linux环境下写个对应种子的随机数序列，再按照赢的方式输入即可。

## move your heart

main函数跟第二题思路相同，略去。

```c
ssize_t back()
{
  char buf[32]; // [rsp+0h] [rbp-20h] BYREF

  printf("gift:%p\n", buf);
  return read(0, buf, 0x30uLL);
}
```

这里是栈迁移。payload大概是

`p64(pop_rdi)+p64(buf+0x18)+p64(system_plt)+b'/bin/sh\0'+p64(buf)+p64(leave_ret)`

刚刚够用。

## checkin

比较有意思，考了整数溢出与异常处理。

### int overflow

```c
int __cdecl main(int argc, const char **argv, const char **envp)
{
  char nptr[32]; // [rsp+0h] [rbp-50h] BYREF
  char buf[44]; // [rsp+20h] [rbp-30h] BYREF
  size_t nbytes; // [rsp+4Ch] [rbp-4h]

  in1t(argc, argv, envp);
  puts("name: ");
  read(0, buf, 0x10uLL);
  buf[16] = 0;
  puts("Please input size: ");
  read(0, nptr, 8uLL);
  if ( atoi(nptr) > 32 || nptr[0] == '-' )
  {
    puts("No!!Hacker");
    exit(0);
  }
  LODWORD(nbytes) = atoi(nptr);
  read(0, nptr, (unsigned int)nbytes);
  return 0;
}
```

buf这个没什么用，暂时不管它。

注意到倒数第二行这里把字节转成了无符号类型，而`atoi`是转成`int`，考虑到有一个整数溢出。

而第0位不能是符号，可以加一个空格来绕过，不影响`atoi`的结果。

### sigsegv

此时我们可以读入无限制长度的数据，可以使用rop等方式解决。

但注意到`1nit`函数里有一个`sigsegv_handler`，意思是`SIGSEGV`后直接吐flag。

```c
void __noreturn sigsegv_handler()
{
  fprintf(stderr, "%s\n", flag);
  fflush(stderr);
  exit(1);
}
```

因此只需乱输一通爆栈即可。

## int_0x80

```c
int __cdecl main(int argc, const char **argv, const char **envp)
{
  int i; // [rsp+Ch] [rbp-124h]
  char buf[264]; // [rsp+10h] [rbp-120h] BYREF
  unsigned __int64 v6; // [rsp+118h] [rbp-18h]

  v6 = __readfsqword(0x28u);
  initial(argc, argv, envp);
  mmap((void *)0x10000, 0x1000uLL, 7, 34, -1, 0LL);
  puts("hello pwn");
  read(0, buf, 0x100uLL);
  for ( i = 0; i < strlen(buf) - 1; ++i )
  {
    if ( ((*__ctype_b_loc())[buf[i]] & 0x4000) == 0 )
      exit(0);
  }
  strcpy((char *)0x10000, buf);
  MEMORY[0x10000]();
  return 0;
}
```

alphanumeric shellcode

可以使用AE64库，记得设一下参数为rsi。

## fakehero

~~建议改名为fakeheap~~（顾名思义，一个伪堆题）。

### add操作

```c
__int64 __fastcall add(void **a1)
{
  void **v1; // rbx
  int v3; // [rsp+1Ch] [rbp-124h] BYREF
  char buf[268]; // [rsp+20h] [rbp-120h] BYREF
  __int64 size[2]; // [rsp+12Ch] [rbp-14h] BYREF

  v3 = 0;
  puts("Hi! Welcome to UNCTF!");
  puts("index: ");
  __isoc99_scanf("%u", &v3);
  puts("Size: ");
  __isoc99_scanf("%u", size);
  if ( LODWORD(size[0]) > 0x100 )
    error();
  v1 = &a1[v3];
  *v1 = malloc(LODWORD(size[0]));
  puts("Content: ");
  read(0, buf, 0x100uLL);
  memcpy(a1[v3], buf, LODWORD(size[0]));
  return 0LL;
}
```

注意这里的buf是从栈上直接copy，并且没有清零，因此可以泄露libc和elf地址。~~但这并没有什么作用~~

更重要的漏洞是没有限制idx的range。

### free&show操作

```c
__int64 __fastcall delete(void **a1)
{
  int v2; // [rsp+1Ch] [rbp-4h] BYREF

  puts("Index: ");
  __isoc99_scanf("%u", &v2);
  if ( !a1[v2] )
    error();
  puts((const char *)a1[v2]);
  free(a1[v2]);
  puts("Don't be far away from me.");
  return 0LL;
}
```

没什么好说的uaf，没有办法编辑free后堆中的内容，再加上前面没有堆溢出，基本无法double free。

### 解法

观察初始化函数，这里堆是可执行的。

```c
void init()
{
  int v0; // [rsp+14h] [rbp-Ch]
  unsigned __int64 ptr; // [rsp+18h] [rbp-8h]

  setbuf(stdin, 0LL);
  setbuf(stdout, 0LL);
  setbuf(stderr, 0LL);
  ptr = (unsigned __int64)malloc(0x1000uLL);
  v0 = sysconf(30);
  if ( v0 == -1 )
    perror("[-] sysconf failed");
  if ( mprotect((void *)(ptr & 0xFFFFFFFFFFFFF000LL), v0, 7) < 0 )
    perror("[-] mprotect failed");
  free((void *)ptr);
}
```

通过动调后发现pointer struct距离ret处较近，可以考虑覆盖ret地址到一个写好shellcode的堆地址，然后退出即可。