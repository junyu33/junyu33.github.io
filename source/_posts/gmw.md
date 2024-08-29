layout: post

title: 从二选一OT到GMW协议的python实现

author: junyu33

mathjax: true

tags:

- crypto

categories: 

- develop

date: 2024-3-16 11:00:00

---

https://github.com/junyu33/GMW-python

<!-- more -->

# implementation

## 2 out of 1 OT

我们先写好通过 socket 连接 Alice 和 Bob 的模板：

- Alice

```python
#!/usr/bin/python3
# alice.py
import socket

# Create a socket object
s = socket.socket()

# Define the port on which you want to connect
port = 12345

# Connect to the server on local computer
s.connect(('127.0.0.1', port))

# Send a message to Bob
s.send(b'Hello Bob!')

# Receive a message from Bob
data = s.recv(1024)
print('Received from Bob:', data.decode())

# Close the connection
s.close()
```

- Bob

```python
#!/usr/bin/python3           
# bob.py
import socket

# Create a socket object
s = socket.socket()

# Define the port on which you want to listen
port = 12345

# Bind to the port
s.bind(('127.0.0.1', port))

# Put the socket into listening mode
s.listen(5)

# Wait for a connection from Alice
c, addr = s.accept()
print('Got connection from', addr)

# Receive a message from Alice
data = c.recv(1024)
print('Received from Alice:', data.decode())

# Send a message to Alice
c.send(b'Hello Alice!')

# Close the connection
c.close()
```

然后由于 socket 的等待时间略为冗长，我们将其缩短为2秒，并将初始化 socket 操作打包为一个函数：

```python
# alice.py
def alice_init():
    # Create a socket object
    s = socket.socket()
    # help reuse the port immediately
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # set a timeout of 2 second
    s.settimeout(2)  
    # Define the port on which you want to connect
    port = 12345
    # Connect to the server on local computer
    s.connect(('127.0.0.1', port))
    return s

# bob.py
def bob_init():
    # Create a socket object
    s = socket.socket()
    # help reuse the port immediately
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # set a timeout of 2 second
    s.settimeout(2)  
    # Define the port on which you want to listen
    port = 12345
    # Bind to the port
    s.bind(('127.0.0.1', port))
    # Put the socket into listening mode
    s.listen(5)
    # Wait for a connection from Alice
    c, addr = s.accept()
    print('Got connection from', addr)
    return c
```

然后准备实现 2 out of 1 OT 协议，显然兰老师在课堂上讲的那个协议不是抵御**半恶意敌手**的，因此我参照[这篇文章](https://zhuanlan.zhihu.com/p/126396795)实现了一个可以抵御的版本，基于求解离散对数的困难性：

简要描述以下协议的原理，我们考虑：

1. Alice 拥有$v_0$,$v_1$, 和密钥 $s,r_0,r_1$
2. Bob 拥有值$i \in \{0,1\}$，和密钥$k$, Bob 想获得$v_i$
3. Alice 和 Bob 事先统一 $g \in \mathbb{Z}_p$，并且 $p$ 是一个大素数，$g$ 是 $p$ 的一个原根。

那么 OT 协议可以通过如下方式演绎：

1. Alice 给 Bob 发送 $g^s$
2. 因为离散对数问题不存在高效接发，Bob 无法破译$s$，但可以基于 $i$ 生成 

$$
\begin{align*}
L_i = \begin{cases}
g^k & \text{if } i=0 \\
g^{s-k} & \text{if } i=1
\end{cases}
\end{align*}
$$

3. Bob 给 Alice 发送 $L_i$，同样，Alice 也无法知道发来的是$g^k$还是$g^{s-k}$，从而无法得到 Bob 选择的 $i$.
4. Alice 生成 $C_0 = (g^{r_0}, L_i^{r_0} \oplus v_0), C_1 = (g^{r_1}, (g^s / L_i)^{r_1} \oplus v_1)$，其中外层括号表示二元组，$\oplus$ 表示按位异或。
5. Alice 给 Bob 发送 $C_0, C_1$，相同原因，Bob 无法破译$r_0, r_1$
6. Bob 解密 $v_i$，分为以下两种情况（这里中括号类似于数组下标）：
    - $i = 0$时, $C_0[0]^k \oplus C_0[1] = (g^{r_0})^k \oplus L_i^{r_0} \oplus v_0 = v_0$；而 Bob 无法解密 $v_1$，因为$C_1[1]=(g^s / L_i)^{r_1} \oplus v_1 = g^{(s-k)r_1} \oplus v_1$，而 Bob 不知道 $s, r_1$.
    - $i = 1$时，$C_1[0]^k \oplus C_1[1] = (g^{r_1})^k \oplus (g^s/L_i)^{r_1} \oplus v_1 = (g^{r_1})^k \oplus (g^k)^{r_1} \oplus v_1 = v_1$；而 Bob 无法解密 $v_0$，因为$C_0[1]=(g^s / L_i)^{r_1} \oplus v_1 = g^{(s-k)r_1} \oplus v_1$，而 Bob 不知道 $s, r_1$.
    - 因此，Bob只能解密$v_i$，而不能解密$v_{1-i}$.


```python
# alice.py
# STEP 1: Alice -> Bob: gs = g**s
alice_send(alice_sock, pow(g, s, p))

# STEP 3: Bob -> Alice: Li
Li = alice_recv(alice_sock)

# Step 4: generate C0, C1
# C0 = (g**r0, Li**r0 ^ v0)
# C1 = (g**r1, (gs/Li)**r1 ^ v1)
C0 = (pow(g, r0, p), pow(Li, r0, p) ^ v0)
C1 = (pow(g, r1, p), pow(pow(g, s, p) * inv(Li, p) % p, r1, p) ^ v1)

# Step 5: Alice -> Bob: C0, C1
alice_send_json(alice_sock, json.dumps([C0, C1]))
```

```python
# bob.py
# STEP 1: Alice -> Bob : g**s 
gs = bob_recv(bob_sock)

# STEP 2: generate Li = g**k when i = 0, g**(s-k) otherwise
Li = 0
if i == 0:
    Li = pow(g, k, p)
else:
    Li = gs * pow(g, -k, p) % p

# STEP 3: Bob -> Alice : Li
bob_send(bob_sock, Li)

# STEP 5: Alice -> Bob : C0, C1
C0C1 = alice_recv_json(bob_sock)
C0 = C0C1[0]
C1 = C0C1[1]

# STEP 6: Bob decrypt v_i
# if i = 0, v0 = C0[0] ** k ^ C0[1]
# if i = 1, v1 = C1[0] ** k ^ C1[1]
v = 0
if i == 0:
    v = pow(C0[0], k, p) ^ C0[1]
else:
    v = pow(C1[0], k, p) ^ C1[1]
print('v_' + str(i) + ' =', v)
```

最后，为了方便之后代码的编写，我们可以将先前的代码 OOP 化：

```python
class Alice_2in1_OT:
    # v0, v1 -> two numbers
    def __init__(self, p, g, v0, v1):
        self.p = p
        self.g = g
        self.s = random.randint(1, p-1)
        self.r0 = random.randint(1, p-1)
        self.r1 = random.randint(1, p-1)
        self.v0 = v0 
        self.v1 = v1
        self.sock = self.init_socket()

    def inv(self, x):
        return pow(x, -1, self.p)

    def init_socket(self):
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(2)
        port = 12345
        s.connect(('127.0.0.1', port))
        return s

    def send_number(self, number):
        self.sock.send(str(number).encode())

    def recv_number(self):
        return int(self.sock.recv(1024).decode())

    def send_json(self, data):
        self.sock.send(json.dumps(data).encode())

    def recv_json(self):
        return json.loads(self.sock.recv(1024).decode())

    def run_protocol(self):
        # STEP 1: Alice -> Bob: gs = g**s
        self.send_number(pow(self.g, self.s, self.p))
        
        # STEP 3: Bob -> Alice: Li
        Li = self.recv_number()

        # Step 4: generate C0, C1
        C0 = (pow(self.g, self.r0, self.p), pow(Li, self.r0, self.p) ^ self.v0)
        C1 = (pow(self.g, self.r1, self.p), pow(pow(self.g, self.s, self.p) * self.inv(Li) \
        % self.p, self.r1, self.p) ^ self.v1)

        # Step 5: Alice -> Bob: C0, C1
        self.send_json([C0, C1])

        # Close the connection
        self.sock.close()
```

```python
class Bob_2in1_OT:
    # i -> which one to choose
    def __init__(self, p, g, i):
        self.p = p
        self.g = g
        self.i = i
        self.k = random.randint(1, p-1)
        self.sock = self.init_socket()

    def inv(self, x):
        return pow(x, -1, self.p)

    def init_socket(self):
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(2)
        port = 12345
        s.bind(('127.0.0.1', port))
        s.listen(5)
        c, addr = s.accept()
        print('Got connection from', addr)
        return c

    def send_number(self, number):
        self.sock.send(str(number).encode())

    def recv_number(self):
        return int(self.sock.recv(1024).decode())

    def send_json(self, data):
        self.sock.send(json.dumps(data).encode())

    def recv_json(self):
        return json.loads(self.sock.recv(1024).decode())

    def run_protocol(self):
        # STEP 1: Alice -> Bob : g**s 
        gs = self.recv_number()

        # STEP 2: generate Li = g**k when i = 0, g**(s-k) otherwise
        if self.i == 0:
            Li = pow(self.g, self.k, self.p)
        else:
            Li = gs * pow(self.g, -self.k, self.p) % self.p

        # STEP 3: Bob -> Alice : Li
        self.send_number(Li)

        # STEP 5: Alice -> Bob : C0, C1
        C0C1 = self.recv_json()
        C0 = C0C1[0]
        C1 = C0C1[1]

        # STEP 6: Bob decrypt v_i
        if self.i == 0:
            v = pow(C0[0], self.k, self.p) ^ C0[1]
        else:
            v = pow(C1[0], self.k, self.p) ^ C1[1]
        print('v_' + str(self.i) + ' =', v)

        # Close the connection
        self.sock.close()
```

## 2 out of 1 -> n out of 1 OT

我们考虑 Alice 持有 $x_1, \ldots, x_n \in \{0, 1\}$，Bob持有$i \in \{1, \ldots, n\}$。通过$OT_1^n$，Bob获得 $x_i$ 但Alice不知道 $i$.

$OT_1^n$ 由以下几步组成：

1. Alice 生成 $k_0 = 0$，随机生成 $k_j \in \{0,1\}$，$j = 1, \ldots, n$.
2. 第二步, Alice 和 Bob 进行 $n$ 次 $O T_1^2$ 操作。在第 $j$ 次操作中, Alice 提供 $k_0 \oplus \cdots \oplus k_{j-1} \oplus x_j$和 $k_j$ 。若 $j=i$, Bob 选择前者; 若 $j \neq i$, Bob 选择后者。
3. 第三步, Bob 通过第 1 次至第 $i-1$ 次 $O T_1^2$ 获得的 $\left\{k_0, \ldots, k_{i-1}\right\}$, 以及第 $i$ 次获得的 $k_0 \oplus \cdots \oplus k_{i-1} \oplus x_i$ 即可解密 $x_i$ 。

我们来分析上述 $O T_1^n$ 的安全性。Bob 的安全性可直接继承自 $O T_1^2$ 的安全性, 即 $O T_1^2$ 保证了 Alice 无从知晓 Bob 在每一轮选择了前者还是后者, 所以 Alice 无从知晓 $i$ 的真实值。Alice 的安全性可以通过分类讨论的方法来论证。我们考虑 Bob 在第 $i$ 轮 $O T_1^2$ 第一次选择了前者。对于 $j<i$ , Bob 在 $O T_1^2$ 中选择的是 $k_j$ ，从而不会获得任何 $x_j$ 的信息。对于 $j>i$, Bob 最多只能获得 $x_j \oplus k_i \oplus \text{others}$ , 由于 Bob 不知道 Alice 随机生成的 $k_i$, 从而无从知晓 $x_j$ 。

该实现的时间复杂度为$O(n)$.

按照[该链接](https://zhuanlan.zhihu.com/p/237061306)的讲义，我们可以较为轻松的写出根据 2 out of 1 OT 拓展为 n out of 1 OT 的代码。有了 2in1 这一层的抽象，nin1 的实现就要简单得多了：

```python
class Alice_nin1_OT:
    def __init__(self, n, x : list):
        self.n = n
        self.x = [0] # add a dummy value to make the index start from 1
        self.x.extend(x)
        self.k = [0]
        for i in range(self.n):
            self.k.append(random.randint(0, 1))

    def run_protocol(self):
        # alice and bob perform the 2-in-1 OT protocol for n times
        v0 = self.x[0] 
        for j in range(1, self.n + 1):
            # v0 = k0 xor k1 xor ... xor k_{j-1} xor x[j]
            v0 ^= self.k[j-1] ^ self.x[j-1] ^ self.x[j] 
            # v1 = k[j]
            v1 = self.k[j]

            alice = Alice_2in1_OT(p, g, v0, v1, 20000+j) # avoid port conflict
            alice.run_protocol()
```

```python
class Bob_nin1_OT:
    def __init__(self, n, i):
        self.n = n
        self.i = i
    
    def run_protocol(self):
        # alice and bob perform the 2-in-1 OT protocol for n times
        k = [] 
        # if j == i, bob choose k0 xor k1 xor ... xor k_{j-1} xor x[j]
        # otherwise, bob choose kj
        for j in range(1, self.n + 1):
            if j == self.i:
                bob = Bob_2in1_OT(p, g, 0, 20000+j) 
                k.append(bob.run_protocol())
            else:
                bob = Bob_2in1_OT(p, g, 1, 20000+j)
                k.append(bob.run_protocol())
        
        # with a little calculation we know 
        # the xor sum of first i elements of k is x[i]
        xi = 0
        for j in range(0, self.i):
            xi ^= k[j]
        return xi
```

为了求稳起见，我先测试了连续两次进行 2 in 1 OT 情况，此时出现了与socket连接有关的错误，具体报错如下：

```python
~/Desktop/old_desktop/scu/新技术专题/code master !2                                 21:03:47 
> python3 alice.py                                                                           
Traceback (most recent call last):                                                           
  File "/run/media/junyu33/develop/tmp1/scu/新技术专题/code/alice.py", line 90, in <module>    
    alice = Alice_2in1_OT(p, g, 4, 0, 20100)   
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^   
  File "/run/media/junyu33/develop/tmp1/scu/新技术专题/code/alice.py", line 18, in __init__    
    self.sock = self.init_socket(self.port)    
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^    
  File "/run/media/junyu33/develop/tmp1/scu/新技术专题/code/alice.py", line 27, in init_socket
    s.connect(('127.0.0.1', port))             
ConnectionRefusedError: [Errno 111] Connection refused 
```

从而导致Bob这边也会报 timeout 的错误：

```python
~/Desktop/old_desktop/scu/新技术专题/code master !2                                    21:03:47                                                                                               
> python3 bob.py                                                                                                                                                                              
Got connection from ('127.0.0.1', 46132)                                                                                                                                                      
4                                                                                                                                                                                             
Traceback (most recent call last):                                                                                                                                                            
  File "/run/media/junyu33/develop/tmp1/scu/新技术专题/code/bob.py", line 105, in <module>                                                                                                    
    bob = Bob_2in1_OT(p, g, 0, 20000)                                                                                                                                                         
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^                                                                                                                                                         
  File "/run/media/junyu33/develop/tmp1/scu/新技术专题/code/bob.py", line 15, in __init__                                                                                                     
    self.sock = self.init_socket(self.port)                                                     
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^                                                     
  File "/run/media/junyu33/develop/tmp1/scu/新技术专题/code/bob.py", line 26, in init_socket    
    c, addr = s.accept()                                                                        
              ^^^^^^^^^^                                                                        
  File "/usr/lib/python3.11/socket.py", line 294, in accept                                     
    fd, addr = self._accept()                                                                   
               ^^^^^^^^^^^^^^                                                                   
TimeoutError: timed out   
```

我仔细观察了一下错误信息，发现第一次的 OT 是没有问题的。我猜想问题出在了关闭 socket 连接后马上又重新打开连接时会拒绝访问（可能是 socket 的冷却时间（2s，定义于`__init__`方法）还没到就进行了下一次连接）。方便起见，我把 socket 连接抽出来，作为函数参数导入进 `Alice_nin1_OT` 和 `Bob_nin1_OT` 类，并删除了`run_protocol()`中关闭socket连接的代码，问题得到解决。 

## GMW protocol

按照[上个链接](https://zhuanlan.zhihu.com/p/237061306)的讲义，我们可以实现一个简单的安全多方计算的协议。这里选取的电路$G$即解决百万富翁问题的电路（如果 $a \ge b$ 输出$1$，反之输出$0$），具体的电路实现如下：

```python
def AND(a, b):
    return a & b

def OR(a, b):
    return a | b

def NOT(a):
    return int(not a)

def G(bit1, bit2):
    not_bit1 = NOT(bit1)
    result = AND(not_bit1, bit2)
    return NOT(result)
```

我们考虑最基础的情况, Alice 和 Bob 拥有一个比特的输入 $x, y \in\{0,1\}$, 他们想计算 $w=G(x, y)$, 其中 $G$ 是一个逻辑门电路。在这个情况下, GMW Protocol 包含如下步骤。

1. Alice 随机生成 $x_a \in\{0,1\}$, 并发送 $x_b=x \oplus x_a$ 给 Bob。我们将 $\left\{x_a, x_b\right\}$ 称为 $x$ 的分享值。由于 $x_a$ 的随机性, Bob 无法破译 $x$ 。
2. Bob 随机生成 $y_b \in\{0,1\}$, 并发送 $y_a=y \oplus y_b$ 给 Alice。由于 $y_b$ 的随机性, Alice 无法破译 $y$ 。
3. Alice 随机生成 $z_a \in\{0,1\}$, 并枚举 $f\left(x_b, y_b\right)=z_a \oplus G\left(x_a \oplus x_b, y_a \oplus y_b\right)$ 的所有可能值。由于 $x_b, y_b \in\{0,1\}$, 所以 $f\left(x_b, y_b\right)$ 一共有四个可能值, 即 $\{f(0,0), f(0,1), f(1,0), f(1,1)\}$ 。
4. Alice 和 Bob 进行 $O T_1^4$ 。Alice 提供 $\{f(0,0), f(0,1), f(1,0), f(1,1)\}$, Bob 提供 $\left(x_b, y_b\right)$所对应的 $i$ 值。 $O T_1^4$ 保证了 Bob 只获得最终结果 $f\left(x_b, y_b\right)$, 以及 Alice 无从知晓 $i$ 从而无从知晓 $x_b, y_b, f\left(x_b, y_b\right)$ 。
5. Bob 将 $z_b=f\left(x_b, y_b\right)$ 。
6. Alice 和 Bob 可以 reveal $z_a, z_b$ 来获得 $z$ 的真实值。不难验证，
$$
z_a \oplus z_b=z_a \oplus z_a \oplus G\left(x_a \oplus x_b, y_a \oplus y_b\right)=G\left(x_a \oplus x_b, y_a \oplus y_b\right)=G(x, y)=z
$$

按照以上的步骤描述，我们可以写出GMW协议的具体实现：

```python
    def run_protocol(self):
        # step1: alice gen xa in [0, 1], xb = x xor xa, sned xb to bob
        xa = random.randint(0, 1)
        xb = self.x ^ xa
        self.send_number(xb)
        
        # step2: bob gen yb in [0, 1], ya = y xor yb, send ya to alice
        ya = self.recv_number()

        # step3: alice gen za in [0, 1], enum f(xb, yb) = za xor G(xa^xb, ya^yb)
        za = random.randint(0, 1)
        f00 = za ^ G(xa^0, ya^0)
        f01 = za ^ G(xa^0, ya^1)
        f10 = za ^ G(xa^1, ya^0)
        f11 = za ^ G(xa^1, ya^1)

        # step4: operate 4 in 1 OT with bob, 
        # alice provide f00 to f11, 
        # bob provide index according to xb*2+yb
        alice = Alice_nin1_OT(4, [f00, f01, f10, f11], self.sock)
        alice.run_protocol()

        # step5: bob send zb = f(xb, yb) to alice
        zb = self.recv_number()

        # step6: alice and bob reveal G(x, y) = za xor zb
        self.send_number(za)
        z = za ^ zb
        return z
```

```python
    def run_protocol(self):
        # step1: alice gen xa in [0, 1], xb = x xor xa, sned xb to bob
        xb = self.recv_number()
        
        # step2: bob gen yb in [0, 1], ya = y xor yb, send ya to alice
        yb = random.randint(0, 1)
        ya = self.y ^ yb
        self.send_number(ya)

        # step4: operate 4 in 1 OT with bob, alice provide 
        # f00 to f11, bob provide index according to xb*2+yb
        i = xb*2 + yb + 1 # don't forget to add 1, it's 1-indexed
        bob = Bob_nin1_OT(4, i, self.sock)
        zb = bob.run_protocol()

        # step5: bob send zb = f(xb, yb) to alice
        self.send_number(zb)

        # step6: alice and bob reveal G(x, y) = za xor zb
        za = self.recv_number()
        z = za ^ zb
        return z
```

经过测试发现可以一次性成功运行，这样我们就实现了一个完整的GMW协议。

## 对 GMW protocol 的改进

当然，这份代码作为一份大作业的话，工作量似乎还不太够。因此我接着打算把这份代码扩展到更多 bit 的比较，并添加加法功能。

### 比较多位

首先我打算$256$以内数的比较，根据大二上期所学的数电知识，我还能依稀回忆起多位比较器的电路实现。因此，我写出了以下 python 代码：

```python
def XOR(a, b):
    return OR(AND(a, NOT(b)), AND(NOT(a), b))

# 按位比较 bit1 > bit2
def g_perbit(bit1, bit2):
    not_bit2 = NOT(bit2)
    return AND(bit1, not_bit2)

# 按位比较 bit1 == bit2
def e_perbit(bit1, bit2):
    return NOT(XOR(bit1, bit2))

# 按位比较 bit1 >= bit2
def ge_perbit(bit1, bit2):
    not_bit1 = NOT(bit1)
    result = AND(not_bit1, bit2)
    return NOT(result)

# little endian
def G_compare(x : list, y : list):
    result0 = ge_perbit(x[0], y[0])
    result1 = OR(g_perbit(x[1], y[1]), AND(e_perbit(x[1], y[1]), result0))
    result2 = OR(g_perbit(x[2], y[2]), AND(e_perbit(x[2], y[2]), result1))
    result3 = OR(g_perbit(x[3], y[3]), AND(e_perbit(x[3], y[3]), result2))
    result4 = OR(g_perbit(x[4], y[4]), AND(e_perbit(x[4], y[4]), result3))
    result5 = OR(g_perbit(x[5], y[5]), AND(e_perbit(x[5], y[5]), result4))
    result6 = OR(g_perbit(x[6], y[6]), AND(e_perbit(x[6], y[6]), result5))
    return OR(g_perbit(x[7], y[7]), AND(e_perbit(x[7], y[7]), result6))
```

此时网上似乎没有讲义给我参考，我得自己魔改协议实现多位比较的功能。首先，我得把输入转化成八根`wire`的形式，这里使用`list`来表示：

```python
    def number2list(self, number):
        res = []
        for i in range(comm_bit):
            res.append(number & 1)
            number >>= 1
        return res
```


然后我需要调用一次$OT_1^{65536}$：

```python
        # alice.py
        f = []

        for possible_xb in range(256):
            for possible_yb in range(256):
                xa_xor_xb_list = self.number2list(xa^possible_xb)
                ya_xor_yb_list = self.number2list(ya^possible_yb)
                f.append(za ^ G_compare(xa_xor_xb_list, ya_xor_yb_list))

        # step4: operate 65536 in 1 OT with bob, alice provide f00 to f{255}{255}, 
        # bob provide index according to xb*256+yb
        alice = Alice_nin1_OT(65536, f, self.sock)
        alice.run_protocol()
```

并修改$x_a, y_b$的初始随机范围：

```python
        # alice.py
        xa = random.randint(0, 255)
```

```python
        # bob.py
        yb = random.randint(0, 255)
```

实验证明，我对 python 的执行效率过于乐观，等待了2分钟也没有输出结果。于是我通过二分法，发现在$[0,31]$以内的比较，python的执行速度可以接受，大概在45秒左右。

### 增加模 32 的加法功能

在数电课程中，我们都学过全加器的实现方式：

```python
def sum_perbit(bit1, bit2, carry_in):
    result = XOR(bit1, XOR(bit2, carry_in))
    carry_out = OR(AND(bit1, bit2), AND(XOR(bit1, bit2), carry_in))
    return result, carry_out
```

因此多位全加也很简单：

```python
# little endian
def G_sum(x : list, y : list):
    result0, carry0 = sum_perbit(x[0], y[0], 0)
    result1, carry1 = sum_perbit(x[1], y[1], carry0)
    result2, carry2 = sum_perbit(x[2], y[2], carry1)
    result3, carry3 = sum_perbit(x[3], y[3], carry2)
    result4, carry4 = sum_perbit(x[4], y[4], carry3)
    return [result0, result1, result2, result3, result4]
```

因为输出是一个列表，我们还需要在 Alice 处实现一个将 `wire` 转换为数字的函数：

```python
    def list2number(self, l):
        res = 0
        for i in range(comm_bit):
            res += l[i] * (2**i)
        return res
```

很可惜，我最初在这个函数的实现写了个bug（准确来说是加的顺序写反了，写成了`res <<= 1; res += l[i]`）,导致我调试了20分钟。我还一度以为 GMW 协议的电路不能实现加法运算，~~因为异或和加法不满足分配律~~，结果还是自己代码写错了，唉。

在修改$x_a, y_a$ 的基础上，因为此时$G(x,y)$的值扩展到了$[0, 31]$，$z_a$的值也应当扩展。为了方便修改，我将输入的 bit 数定义为`comm_bit`（此时应当为$5$），最终 Alice 端协议实现如下，Bob 的代码无需变化。

```python
    def run_sum_protocol(self):
        # step1: alice gen xa in [0, 2**comm_bit-1], xb = x xor xa, sned xb to bob
        xa = random.randint(0, 2**comm_bit-1)
        xb = self.x ^ xa
        self.send_number(xb)
        
        # step2: bob gen yb in [0, 2**comm_bit-1], ya = y xor yb, send ya to alice
        ya = self.recv_number()

        # step3: alice gen za in [0, 1], enum f(xb, yb) = za xor G(xa^xb, ya^yb)
        za = random.randint(0, 2**comm_bit-1)

        f = []

        for possible_xb in range(2**comm_bit):
            for possible_yb in range(2**comm_bit):
                xa_xor_xb_list = self.number2list(xa^possible_xb)
                ya_xor_yb_list = self.number2list(ya^possible_yb)
                sum_list = G_sum(xa_xor_xb_list, ya_xor_yb_list)
                f.append(za ^ self.list2number(sum_list))

        # step4: operate 4**comm_bit in 1 OT with bob, alice provide f00 
        # to f{2**comm_bit-1}{2**comm_bit-1}, 
        # bob provide index according to xb*(2**comm_bit)+yb
        alice = Alice_nin1_OT(4**comm_bit, f, self.sock)
        alice.run_protocol()

        # step5: bob send zb = f(xb, yb) to alice
        zb = self.recv_number()

        # step6: alice and bob reveal G(x, y) = za xor zb
        self.send_number(za)
        z = za ^ zb
        return z
```

因此，整个 GMW 的实现就大功告成了，接下来贴出最终代码：

- gates

```python
#!/usr/bin/python3           
# gates.py
def AND(a, b):
    return a & b

def OR(a, b):
    return a | b

def NOT(a):
    return int(not a)

def XOR(a, b):
    return OR(AND(a, NOT(b)), AND(NOT(a), b))

def g_perbit(bit1, bit2):
    not_bit2 = NOT(bit2)
    return AND(bit1, not_bit2)

def e_perbit(bit1, bit2):
    return NOT(XOR(bit1, bit2))

def ge_perbit(bit1, bit2):
    not_bit1 = NOT(bit1)
    result = AND(not_bit1, bit2)
    return NOT(result)


def sum_perbit(bit1, bit2, carry_in):
    result = XOR(bit1, XOR(bit2, carry_in))
    carry_out = OR(AND(bit1, bit2), AND(XOR(bit1, bit2), carry_in))
    return result, carry_out

# little endian
def G_compare(x : list, y : list):
    result0 = ge_perbit(x[0], y[0])
    result1 = OR(g_perbit(x[1], y[1]), AND(e_perbit(x[1], y[1]), result0))
    result2 = OR(g_perbit(x[2], y[2]), AND(e_perbit(x[2], y[2]), result1))
    result3 = OR(g_perbit(x[3], y[3]), AND(e_perbit(x[3], y[3]), result2))
    result4 = OR(g_perbit(x[4], y[4]), AND(e_perbit(x[4], y[4]), result3))
    #result5 = OR(g_perbit(x[5], y[5]), AND(e_perbit(x[5], y[5]), result4))
    #result6 = OR(g_perbit(x[6], y[6]), AND(e_perbit(x[6], y[6]), result5))
    #return OR(g_perbit(x[7], y[7]), AND(e_perbit(x[7], y[7]), result6))
    return result4

# little endian
def G_sum(x : list, y : list):
    result0, carry0 = sum_perbit(x[0], y[0], 0)
    result1, carry1 = sum_perbit(x[1], y[1], carry0)
    result2, carry2 = sum_perbit(x[2], y[2], carry1)
    result3, carry3 = sum_perbit(x[3], y[3], carry2)
    result4, carry4 = sum_perbit(x[4], y[4], carry3)
    return [result0, result1, result2, result3, result4]
```

- Alice

```python
#!/usr/bin/python3
# alice.py
import socket
import json
import random
import sys
from gates import G_compare, G_sum

def init_socket(ip, port):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.settimeout(60)
    s.connect((ip, port))
    return s


class Alice_2in1_OT:
    def __init__(self, p, g, v0, v1, sock):
        self.p = p
        self.g = g
        self.s = random.randint(1, p-1)
        self.r0 = random.randint(1, p-1)
        self.r1 = random.randint(1, p-1)
        self.v0 = v0
        self.v1 = v1
        self.sock = sock

    def inv(self, x):
        return pow(x, -1, self.p)

    def send_number(self, number):
        self.sock.send(str(number).encode())

    def recv_number(self):
        return int(self.sock.recv(1024).decode())

    def send_json(self, data):
        self.sock.send(json.dumps(data).encode())

    def recv_json(self):
        return json.loads(self.sock.recv(1024).decode())

    def run_protocol(self):
        # STEP 1: Alice -> Bob: gs = g**s
        self.send_number(pow(self.g, self.s, self.p))

        # STEP 3: Bob -> Alice: Li
        Li = self.recv_number()

        # Step 4: generate C0, C1
        C0 = (pow(self.g, self.r0, self.p), pow(Li, self.r0, self.p) ^ self.v0)
        C1 = (pow(self.g, self.r1, self.p), pow(pow(self.g, self.s, self.p) * self.inv(Li) \
        % self.p, self.r1, self.p) ^ self.v1)

        # Step 5: Alice -> Bob: C0, C1
        self.send_json([C0, C1])


class Alice_nin1_OT:
    def __init__(self, n, x : list, sock):
        self.n = n
        self.x = [0] # add a dummy value to make the index start from 1
        self.x.extend(x)
        self.k = [0]
        for i in range(self.n):
            self.k.append(random.randint(0, 1))
        self.sock = sock

    def run_protocol(self):
        # alice and bob perform the 2-in-1 OT protocol for n times
        v0 = self.x[0] 
        for j in range(1, self.n + 1):
            # v0 = k0 xor k1 xor ... xor k_{j-1} xor x[j]
            v0 ^= self.k[j-1] ^ self.x[j-1] ^ self.x[j] 
            # v1 = k[j]
            v1 = self.k[j]

            alice = Alice_2in1_OT(p, g, v0, v1, self.sock) # avoid port conflict
            alice.run_protocol()


class Alice_GMW:
    def __init__(self, x, sock):
        self.x = x
        self.sock = sock

    def send_number(self, number):
        self.sock.send(str(number).encode())

    def recv_number(self):
        return int(self.sock.recv(1024).decode())

    def number2list(self, number):
        res = []
        for i in range(comm_bit):
            res.append(number & 1)
            number >>= 1
        return res

    def list2number(self, l):
        res = 0
        for i in range(comm_bit):
            res += l[i] * (2**i)
        return res

    def run_protocol(self):
        # step1: alice gen xa in [0, 2**comm_bit-1], xb = x xor xa, sned xb to bob
        xa = random.randint(0, 2**comm_bit-1)
        xb = self.x ^ xa
        self.send_number(xb)
        
        # step2: bob gen yb in [0, 2**comm_bit-1], ya = y xor yb, send ya to alice
        ya = self.recv_number()

        # step3: alice gen za in [0, 1], enum f(xb, yb) = za xor G(xa^xb, ya^yb)
        za = random.randint(0, 1)

        f = []

        for possible_xb in range(2**comm_bit):
            for possible_yb in range(2**comm_bit):
                xa_xor_xb_list = self.number2list(xa^possible_xb)
                ya_xor_yb_list = self.number2list(ya^possible_yb)
                f.append(za ^ G_compare(xa_xor_xb_list, ya_xor_yb_list))

        # step4: operate 4**comm_bit in 1 OT with bob, 
        # alice provide f00 to f{2**comm_bit-1}{2**comm_bit-1}, 
        # bob provide index according to xb*(2**comm_bit)+yb
        alice = Alice_nin1_OT(4**comm_bit, f, self.sock)
        alice.run_protocol()

        # step5: bob send zb = f(xb, yb) to alice
        zb = self.recv_number()

        # step6: alice and bob reveal G(x, y) = za xor zb
        self.send_number(za)
        z = za ^ zb
        return z

    def run_sum_protocol(self):
        # step1: alice gen xa in [0, 2**comm_bit-1], xb = x xor xa, sned xb to bob
        xa = random.randint(0, 2**comm_bit-1)
        xb = self.x ^ xa
        self.send_number(xb)
        
        # step2: bob gen yb in [0, 2**comm_bit-1], ya = y xor yb, send ya to alice
        ya = self.recv_number()

        # step3: alice gen za in [0, 1], enum f(xb, yb) = za xor G(xa^xb, ya^yb)
        za = random.randint(0, 2**comm_bit-1)

        f = []

        for possible_xb in range(2**comm_bit):
            for possible_yb in range(2**comm_bit):
                xa_xor_xb_list = self.number2list(xa^possible_xb)
                ya_xor_yb_list = self.number2list(ya^possible_yb)
                sum_list = G_sum(xa_xor_xb_list, ya_xor_yb_list)
                f.append(za ^ self.list2number(sum_list))

        # step4: operate 4**comm_bit in 1 OT with bob, 
        # alice provide f00 to f{2**comm_bit-1}{2**comm_bit-1}, 
        # bob provide index according to xb*(2**comm_bit)+yb
        alice = Alice_nin1_OT(4**comm_bit, f, self.sock)
        alice.run_protocol()

        # step5: bob send zb = f(xb, yb) to alice
        zb = self.recv_number()

        # step6: alice and bob reveal G(x, y) = za xor zb
        self.send_number(za)
        z = za ^ zb
        return z


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python3 alice.py <mode> <x> [<ip of bob>] [<port>]')
        exit(1)

    mode = sys.argv[1]
    x = int(sys.argv[2])
    port = 12345
    if len(sys.argv) >= 4:
        ip = sys.argv[3]
        if len(sys.argv) >= 5:
            port = int(sys.argv[4])
    else:
        ip = '127.0.0.1'
    sock = init_socket(ip, port)

    # Define the prime number p and generator g
    p = 998244353
    g = 3
    comm_bit = 5


    Alice = Alice_GMW(x, sock)
    if mode == 'c': 
        res = Alice.run_protocol()
    elif mode == 'a':
        res = Alice.run_sum_protocol()
    else:
        print('mode error')
        exit(1)
    print('result from Alice: G(x, y) =', res)
    sock.close()
```

- Bob

```python
#!/usr/bin/python3           
# bob.py
import socket
import random
import json
import sys

def init_socket(ip, port):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.settimeout(2)
    s.bind((ip, port))
    s.listen(5)
    c, addr = s.accept()
    print('Got connection from', addr)
    return c


class Bob_2in1_OT:
    def __init__(self, p, g, i, sock):
        self.p = p
        self.g = g
        self.i = i
        self.k = random.randint(1, p-1)
        self.sock = sock

    def inv(self, x):
        return pow(x, -1, self.p)

    def send_number(self, number):
        self.sock.send(str(number).encode())

    def recv_number(self):
        return int(self.sock.recv(1024).decode())

    def send_json(self, data):
        self.sock.send(json.dumps(data).encode())

    def recv_json(self):
        return json.loads(self.sock.recv(1024).decode())

    def run_protocol(self):
        # STEP 1: Alice -> Bob : g**s 
        gs = self.recv_number()

        # STEP 2: generate Li = g**k when i = 0, g**(s-k) otherwise
        if self.i == 0:
            Li = pow(self.g, self.k, self.p)
        else:
            Li = gs * pow(self.g, -self.k, self.p) % self.p

        # STEP 3: Bob -> Alice : Li
        self.send_number(Li)

        # STEP 5: Alice -> Bob : C0, C1
        C0C1 = self.recv_json()
        C0 = C0C1[0]
        C1 = C0C1[1]

        # STEP 6: Bob decrypt v_i
        if self.i == 0:
            v = pow(C0[0], self.k, self.p) ^ C0[1]
        else:
            v = pow(C1[0], self.k, self.p) ^ C1[1]
        # print('v_' + str(self.i) + ' =', v)
        return v

class Bob_nin1_OT:
    def __init__(self, n, i, sock):
        self.n = n
        self.i = i
        self.sock = sock
    
    def run_protocol(self):
        # alice and bob perform the 2-in-1 OT protocol for n times
        k = [] 
        # if j == i, bob choose k0 xor k1 xor ... xor k_{j-1} xor x[j]
        # otherwise, bob choose kj
        for j in range(1, self.n + 1):
            if j == self.i:
                bob = Bob_2in1_OT(p, g, 0, self.sock) 
                k.append(bob.run_protocol())
            else:
                bob = Bob_2in1_OT(p, g, 1, self.sock)
                k.append(bob.run_protocol())
        
        # with a little calculation we know 
        # the xor sum of first i elements of k is x[i]
        xi = 0
        for j in range(0, self.i):
            xi ^= k[j]
        return xi

class Bob_GMW:
    def __init__(self, y, sock):
        self.y = y
        self.sock = sock

    def send_number(self, number):
        self.sock.send(str(number).encode())

    def recv_number(self):
        return int(self.sock.recv(1024).decode())

    def run_protocol(self):
        # step1: alice gen xa in [0, 2**comm_bit-1], xb = x xor xa, sned xb to bob
        xb = self.recv_number()
        
        # step2: bob gen yb in [0, 2**comm_bit-1], ya = y xor yb, send ya to alice
        yb = random.randint(0, 2**comm_bit-1)
        ya = self.y ^ yb
        self.send_number(ya)

        # step4: operate 4**comm_bit in 1 OT with bob,
        # alice provide f00 to f{2**comm_bit-1}{2**comm_bit-1}, 
        # bob provide index according to xb*(2**comm_bit)+yb
        i = xb*(2**comm_bit) + yb + 1 # don't forget to add 1, it's 1-indexed
        bob = Bob_nin1_OT(4**comm_bit, i, self.sock)
        zb = bob.run_protocol()

        # step5: bob send zb = f(xb, yb) to alice
        self.send_number(zb)

        # step6: alice and bob reveal G(x, y) = za xor zb
        za = self.recv_number()
        z = za ^ zb
        return z

        
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python3 bob.py <mode> <y> [<ip of bob>] [<port>]')
        sys.exit(1)
    
    mode = sys.argv[1]
    y = int(sys.argv[2])
    port = 12345
    if len(sys.argv) >= 4:
        ip = sys.argv[3]
        if len(sys.argv) >= 5:
            port = int(sys.argv[4])
    else:
        ip = '127.0.0.1'
    sock = init_socket(ip, port)
    
    # Define the prime number p and generator g
    p = 998244353
    g = 3
    comm_bit = 5


    Bob = Bob_GMW(y, sock)
    res = Bob.run_protocol()
    print('result from Bob: G(x, y) =', res)
    sock.close()
```

# References

- [混淆电路介绍（一）不经意传输](https://zhuanlan.zhihu.com/p/126396795)
- [GMW Protocol 介绍](https://zhuanlan.zhihu.com/p/237061306)
