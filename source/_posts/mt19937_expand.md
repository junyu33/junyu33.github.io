layout: post
title: 广义mt19937随机数逆向
author: junyu33
mathjax: true
tags: 

- crypto
- python

categories:

  - ctf

date: 2022-1-22 22:30:00

---

# 题意简述

给出mt19937中的10个参数$ N、M、A、U、S、B、T、C、L、F $，并给出__刚刚生成__的前$ N $个伪随机数，求出伪随机数对应的种子seed。

<!-- more -->

# 思路分析

## 20pts

暴力枚举seed即可，代码略。

## 100pts

做法的大致思路是：生成的随机数→```twist```后的```state```→```twist```前可能的```state[-1]```→求得seed


我们先考虑标准情况，也就是参数与论文完全一致的时候，这里有一篇[现成的题解](http://blog.tolinchan.xyz/2021/07/27/%E6%A2%85%E6%A3%AE%E6%97%8B%E8%BD%AC%E7%AE%97%E6%B3%95%E7%A0%94%E7%A9%B6/)。

具体原理这里就不阐释了，给的链接和[Mivik的题解](https://mivik.gitee.io/2020/solution/mivik-newbie-and-chinos-contest-2020-solution-amegura/)叙述得很清楚。

然后当$A$的首位不为1时，就不能直接通过```tmp```的首位判断原来的```tmp```是不是奇数了。

原题解中逆向```twist```的代码如下：

```python
def backtrace(cur):
    high = 0x80000000
    low = 0x7fffffff
    mask = 0x9908b0df
    state = cur
    for i in range(623,-1,-1):
        tmp = state[i]^state[(i+397)%624]
        # recover Y,tmp = Y
        if tmp & high == high:
            tmp ^= mask
            tmp <<= 1
            tmp |= 1
        else:
            tmp <<=1
        # recover highest bit
        res = tmp&high
        # recover other 31 bits,when i =0,it just use the method again it so beautiful!!!!
        tmp = state[i-1]^state[(i+396)%624]
        # recover Y,tmp = Y
        if tmp & high == high:
            tmp ^= mask
            tmp <<= 1
            tmp |= 1
        else:
            tmp <<=1
        res |= (tmp)&low
        state[i] = res    
    return state
```

这里的问题就出在```if tmp & high == high:```这个条件判断已经失效，不能据此判定tmp的准确值。

一个简便的做法是枚举```mt[N - 1]```的四种可能，然后由于```mt[i - 1] ^ mt[i - 1] >> 30```可逆，而且因为$F$是奇数，与```2 ** 32``` 必定互质，因此可以通过求$F$的逆元来倒推seed。

检验这四个seed的方式就是用seed再重新生成几个随机数，与输入比对即可。

# 完整代码

```python
from gmpy2 import invert
def _int32(x):
    return int(0xFFFFFFFF & x)
class mt19937:
    def __init__(self, seed=0):# magic method (run code below automatically when an object is created) 
        self.mt = [0] * N
        self.mt[0] = seed
        self.mti = 0
        for i in range(1, N):
            self.mt[i] = _int32(F * (self.mt[i - 1] ^ self.mt[i - 1] >> 30) + i)
    def getstate(self,op=False):
        if self.mti == 0 and op==False:
            self.twist()
        y = self.mt[self.mti]
        y = y ^ y >> U
        y = y ^ y << S & B
        y = y ^ y << T & C
        y = y ^ y >> L
        self.mti = (self.mti + 1) % N
        return _int32(y)
    def twist(self):
        for i in range(0, N):
            y = _int32((self.mt[i] & 0x80000000) + (self.mt[(i + 1) % N] & 0x7fffffff))
            self.mt[i] = (y >> 1) ^ self.mt[(i + M) % N]
            if y % 2 != 0:
                self.mt[i] = self.mt[i] ^ A
    def inverse_right(self,res, shift, mask=0xffffffff, bits=32):
        tmp = res
        for i in range(bits // shift):
            tmp = res ^ tmp >> shift & mask
        return tmp
    def inverse_left(self,res, shift, mask=0xffffffff, bits=32):
        tmp = res
        for i in range(bits // shift):
            tmp = res ^ tmp << shift & mask
        return tmp
    def extract_number(self,y): # namely "temper" in Mivik's code
        y = y ^ y >> U
        y = y ^ y << S & B
        y = y ^ y << T & C
        y = y ^ y >> L
        return y&0xffffffff
    def recover(self,y): # inverse of extract_number
        y = self.inverse_right(y,L)
        y = self.inverse_left(y,T,C)
        y = self.inverse_left(y,S,B)
        y = self.inverse_right(y,U)
        return y&0xffffffff
    def setstate(self,s): # N generated random numbers -> mt[] after twisting 
        if(len(s)!=N):
            raise ValueError("The length of prediction must be N!")
        for i in range(N):
            self.mt[i]=self.recover(s[i])
        #self.mt=s
        self.mti=0
    ''' 
    def predict(self,s): # a method to predict other pseudo random numbers after given N of them (useless in this problem)
        self.setstate(s)
        self.twist()
        return self.getstate(True)
    '''
    def invtwist(self): # mt[] after twisting -> 4 possible values of mt[-1] before twisting
        high = 0x80000000
        low = 0x7fffffff
        mask = A
        opt = [0] * 4
        for i in range(N-1,N-2,-1): # only process the last number
            for s in range(2):
                for t in range(2):
                    tmp = self.mt[i]^self.mt[(i+M)%N]
                    if s==0: # two possibilities
                        tmp ^= mask
                        tmp <<= 1
                        tmp |= 1
                    else:
                        tmp <<=1
                    res = tmp&high
                    tmp = self.mt[i-1]^self.mt[(i+M-1)%N]
                    if t==0: # another two
                        tmp ^= mask
                        tmp <<= 1
                        tmp |= 1
                    else:
                        tmp <<=1
                    res |= (tmp)&low
                    opt[s * 2 + t] = res
        return opt
    
    def recover_seed(self,last): # mt[-1] -> mt[0]
        n = 1 << 32
        inv = invert(F, n) # inverse of F mod 2 ^ 32
        for i in range(N-1, 0, -1):
            last = ((last - i) * inv) % n
            last = self.inverse_right(last, 30)
        return last

N, M, A, U, S, B, T, C, L, F = map(int, input().split())
inpt = [0] * N # align enough space
for i in range (N):
    inpt[i] = int(input())
D = mt19937() 
D.setstate(inpt) # using the input to recover state after twisting
op = D.invtwist() # generate four possibilities of D.mt[-1]
seed = [0] * 4
for i in range(4): # check the seeds one by one
    seed[i] = D.recover_seed(op[i]) 
    E = mt19937(seed[i])
    E.getstate() # another psuedo random number generator
    flag = 1
    for j in range(10): # compare first 10 numbers is totally enough 
        if E.extract_number(E.mt[j]) != inpt[j]:
            flag = 0
    if flag > 0:
        print(seed[i])
        break
```

时间复杂度$ O(N) $。
