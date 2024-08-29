layout: post

title: 有限域中乘法在 intel 指令集上的高性能实现

author: junyu33

tags: 

- crypto
- c

mathjax: true

categories: 

- develop

date: 2024-7-1 22:30:00

---

```c
/* multiplication in galois field with reduction */
#ifdef __x86_64__
__attribute__((target("sse2,pclmul")))
#endif
inline void gfmul (__m128i a, __m128i b, __m128i *res){
	__m128i tmp3, tmp6, tmp7, tmp8, tmp9, tmp10, tmp11, tmp12;
	__m128i XMMMASK = _mm_setr_epi32(0xffffffff, 0x0, 0x0, 0x0);
	mul128(a, b, &tmp3, &tmp6);
	tmp7 = _mm_srli_epi32(tmp6, 31);
	tmp8 = _mm_srli_epi32(tmp6, 30);
	tmp9 = _mm_srli_epi32(tmp6, 25);
	tmp7 = _mm_xor_si128(tmp7, tmp8);
	tmp7 = _mm_xor_si128(tmp7, tmp9);
	tmp8 = _mm_shuffle_epi32(tmp7, 147);

	tmp7 = _mm_and_si128(XMMMASK, tmp8);
	tmp8 = _mm_andnot_si128(XMMMASK, tmp8);
	tmp3 = _mm_xor_si128(tmp3, tmp8);
	tmp6 = _mm_xor_si128(tmp6, tmp7);
	tmp10 = _mm_slli_epi32(tmp6, 1);
	tmp3 = _mm_xor_si128(tmp3, tmp10);
	tmp11 = _mm_slli_epi32(tmp6, 2);
	tmp3 = _mm_xor_si128(tmp3, tmp11);
	tmp12 = _mm_slli_epi32(tmp6, 7);
	tmp3 = _mm_xor_si128(tmp3, tmp12);

	*res = _mm_xor_si128(tmp3, tmp6);
}
```

<!-- more -->

# prerequisite

- 模128阶多项有限域的运算
- intel SSE 指令集
- sagemath 的基本使用

这里的不可约多项式为$x^{128}+x^7+x^2+x+1$.

# mul128

首先讨论在不进行约简时，两个 128 bit 多项式的乘法运算。为了编写方便，我们将多项式转化为对应的二进制数，例如$x^4+x^3+x+1$对应的二进制为`0b11011`，即$27$。

intel 中恰好有一个指令可以实现$\mathbb{F}_{2^n}$的乘法（即非进位乘法，Carry-less Multiplication），即`__m128i _mm_clmulepi64_si128(__m128i a, __m128i b, const int imm8);`。它的语法如下：

- `__m128i a`: 包含两个 64 位整数的源操作数。
- `__m128i b`: 包含两个 64 位整数的源操作数。
- `const int imm8`: 一个立即数，指定应该使用的 64 位整数对。这是一个 8 位常量值：
  - 如果 `imm8` 的最低位为 0，选择 `a` 的低 64 位；否则，选择 `a` 的高 64 位。
  - 如果 `imm8` 的第 4 位为 0，选择 `b` 的低 64 位；否则，选择 `b` 的高 64 位。

我们可以借助64位的非进位乘法来实现128位的非进位乘法，具体步骤如下：

```
/* multiplication in galois field without reduction */
#ifdef __x86_64__
__attribute__((target("sse2,pclmul")))
inline void mul128(__m128i a, __m128i b, __m128i *res1, __m128i *res2) {
	__m128i tmp3, tmp4, tmp5, tmp6;
	tmp3 = _mm_clmulepi64_si128(a, b, 0x00);
	tmp4 = _mm_clmulepi64_si128(a, b, 0x10);
	tmp5 = _mm_clmulepi64_si128(a, b, 0x01);
	tmp6 = _mm_clmulepi64_si128(a, b, 0x11);

	tmp4 = _mm_xor_si128(tmp4, tmp5);
	tmp5 = _mm_slli_si128(tmp4, 8);
	tmp4 = _mm_srli_si128(tmp4, 8);
	tmp3 = _mm_xor_si128(tmp3, tmp5);
	tmp6 = _mm_xor_si128(tmp6, tmp4);
	// initial mul now in tmp3, tmp6
	*res1 = tmp3;
	*res2 = tmp6;
}
```

以下给出该算法的证明：

## 证明

设被乘数$A$的高低位分别为$a_1$和$a_2$，同理乘数$B$的高低位分别为$b_1$和$b_2$。在算法前半段，我们有：

$\mathrm{tmp6} = a_1b_1$

$\mathrm{tmp5} = a_2b_1$

$\mathrm{tmp4} = a_1b_2$

$\mathrm{tmp3} = a_2b_2$  



在后半段，我们有：


$\mathrm{tmp5'} = 2^{64}((\mathrm{tmp4+tmp5})\%2^{64})$

$\mathrm{tmp4'} = \lfloor 2^{-64}(\mathrm{tmp4+tmp5}) \rfloor$

$\mathrm{tmp3'} = 2^{64}((\mathrm{tmp4+tmp5})\%2^{64})+\mathrm{tmp3}$

$\mathrm{tmp6'} = \lfloor 2^{-64}(\mathrm{tmp4+tmp5}) \rfloor + \mathrm{tmp6}$


故：

$res1 + res2$

$= 2^{128}\mathrm{tmp6'}+\mathrm{tmp3'}$

$= 2^{128}\mathrm{tmp6}+2^{128}(2^{-64}(\mathrm{tmp4+tmp5})- 2^{-64}(\mathrm{tmp4+tmp5})\%1)+2^{64}((\mathrm{tmp4+tmp5})\%2^{64})+\mathrm{tmp3}$

$=2^{128}\mathrm{tmp6}+2^{64}(\mathrm{tmp4+tmp5})-2^{64}(\mathrm{tmp4+tmp5})\%2^{128}+2^{64}(\mathrm{tmp4+tmp5})\%2^{128}+\mathrm{tmp3}$

$=2^{128}\mathrm{tmp6}+2^{64}(\mathrm{tmp4+tmp5})+\mathrm{tmp3}$

而：

$A*B$

$=(2^{64}a_1 + a_2)(2^{64}b_1 + b_2)$

$=2^{128}\mathrm{tmp6}+2^{64}(\mathrm{tmp4+tmp5})+\mathrm{tmp3}$

故$res1 + res2 = A*B$

# gfmul

实际上，我们还需要将进行非进位乘法后的结果对$x^{128}+x^7+x^2+x+1$进行约简，而sagemath有专门针对有限域处理的轮子，因此我们可以编写一个sagemath的程序来验证结果：

```python
# 定义有限域上的多项式环
P.<x> = PolynomialRing(GF(2))

# 定义模多项式
mod_poly = x^128 + x^7 + x^2 + x + 1

# 定义有限域 GF(2^128)
K.<a> = GF(2**128, modulus=mod_poly)

# 将整数转换为多项式
def int_to_poly(n):
    bin_str = bin(n)[2:]  # 将整数转换为二进制字符串，去掉'0b'前缀
    return sum([int(bit) * x^i for i, bit in enumerate(reversed(bin_str))])

# 将多项式转换回整数
def poly_to_int(p):
    return sum([int(coeff) * (2**i) for i, coeff in enumerate(p.list())])

# 示例：整数表示的元素
f_int, g_int = 98195696920426533817649554218743231661, 43027262476631949179376797970948942433

# 转换为多项式
f_poly = int_to_poly(f_int)
g_poly = int_to_poly(g_int)

# 在 GF(2^128) 上进行运算
f = K(f_poly)
g = K(g_poly)

# 运算示例
add_result = f + g
mul_result = f * g

# 将结果转换回整数
add_result_int = poly_to_int(add_result.polynomial())
mul_result_int = poly_to_int(mul_result.polynomial())

print("f (as int) =", f_int)
print("g (as int) =", g_int)
print("f + g (as int) =", add_result_int)
print("f * g (as int) =", mul_result_int)
'''
f (as int) = 98195696920426533817649554218743231661
g (as int) = 43027262476631949179376797970948942433
f + g (as int) = 140241067422779931769655503331313065676
f * g (as int) = 30853704161780158484268560045100192027
'''
```

当有了一个正常的对拍程序后，我们就可以分析并调试文章开头给出的代码了。

## 证明

我们先分析，如何用$\mathrm{tmp3, tmp6}$的位运算来表示$\mathbb{F}_{2^{128}}(a*b)$的结果：

```python
tmp3, tmp6 = mul128(a, b)

// 假设 T = ((tmp6 >> 127) ^ (tmp6 >> 126) ^ (tmp6 >> 121))

// 这里的 nr() 表示未约简的意思
res = nr(tmp3 ^ ((tmp6) << 128))
    = tmp3 ^ nr(tmp6 << 128)
    = tmp3 ^ nr(tmp6) ^ nr(tmp6 << 1) ^ nr(tmp6 << 2) ^ nr(tmp6 << 7)
    = tmp3 ^ nr(tmp6) ^ (nr(tmp6) << 1) ^ (nr(tmp6) << 2) ^ (nr(tmp6) << 7)
    // 这里 tmp6 >> 128 肯定是0，所以省略
    = tmp3 ^ (tmp6 ^ T)
           ^ ((tmp6 ^ T) << 1)
           ^ ((tmp6 ^ T) << 2)
           ^ ((tmp6 ^ T) << 7)
```

但事实上为了计算方便，我们取`T = ((tmp6 >> 31) ^ (tmp6 >> 30) ^ (tmp6 >> 25))`，因此我们有：

```python
def gfmul(a, b):
    tmp3, tmp6 = mul128(a, b)
    T = ((tmp6 >> 31) ^ (tmp6 >> 30) ^ (tmp6 >> 25))

    res = tmp3 ^ \
      (T >> 96) ^ tmp6 ^ \
      (((T >> 96) ^ tmp6) << 1) ^ \
      (((T >> 96) ^ tmp6) << 2) ^ \
      (((T >> 96) ^ tmp6) << 7)
    return res % (2 ** 128 - 1)
```

经过与sagemath的比对，它们的输出完全一致。

## 指令集化

但在128bit数中，并没有将一个128bit数直接右移或左移的操作，如果使用C语言的`<<`或者`>>`运算符只会将组成`__m128i`的四个32位向量一起左移或者右移，从而达不到正确的结果。

实际上，这两个运算符对应的是`_mm_slli_epi32`和`_mm_srli_epi32`这两个指令，前者的语法如下，后者类似：

```c
__m128i _mm_slli_epi32(__m128i a, int imm8);
```

>`_mm_slli_epi32` 指令对寄存器 `a` 中的每个 32 位整数执行逻辑左移操作，移位的位数由立即数 `imm8` 指定。所有的整数都按照相同的位数进行左移，移出的高位被丢弃，低位补零。

通过相关推导，对于任何128bit数$x$，我们有以下恒等式($0 < i < 32$)：

`x << i === mm_slli_epi32(x, i) ^ (mm_srli_epi32(x, 32-i) << 32)`

证明比较容易，这里略去。

因此，我们可以修改原来的函数：

```python
def gfmul(a, b):
    tmp3, tmp6 = mul128(a, b)
    T = ((tmp6 >> 31) ^ (tmp6 >> 30) ^ (tmp6 >> 25))
    # T = (srli(tmp6, 31) ^ srli(tmp6, 30) ^ srli(tmp6, 25))

    res = tmp3 ^ \
      (T >> 96) ^ tmp6 ^ \
      (((T >> 96) ^ tmp6) << 1) ^ \
      (((T >> 96) ^ tmp6) << 2) ^ \
      (((T >> 96) ^ tmp6) << 7)

    # res    = tmp3 ^ tmp6 ^ \
    #        = slli(tmp6, 1) ^ (srli(tmp6, 31) << 32) ^ \
    #          slli(tmp6, 2) ^ (srli(tmp6, 30) << 32) ^ \
    #          slli(tmp6, 7) ^ (srli(tmp6, 25) << 32) ^ \
    #          (T >> 96) ^ (T >> 96 << 1) ^ (T >> 96 << 2) ^ (T >> 96 << 7)
    # 这里因为(T >> 96 << 7)本身最多只有14位，比32位小，因此不用进行上文公式的变形
    #        = (T >> 96) ^ tmp6 \
    #          slli(tmp6 ^ (T >> 96), 1) \
    #          slli(tmp6 ^ (T >> 96), 2) \
    #          slli(tmp6 ^ (T >> 96), 7) \
    #          (T << 32) ^ tmp3

    return res & (2 ** 128 - 1)
```

现在我们可以回到本文开头的源码了：

```c
void gfmul (__m128i a, __m128i b, __m128i *res){
	__m128i tmp3, tmp6, tmp7, tmp8, tmp9, tmp10, tmp11, tmp12;
	__m128i XMMMASK = _mm_setr_epi32(0xffffffff, 0x0, 0x0, 0x0);
	mul128(a, b, &tmp3, &tmp6);

	tmp7 = _mm_srli_epi32(tmp6, 31);
	tmp8 = _mm_srli_epi32(tmp6, 30);
	tmp9 = _mm_srli_epi32(tmp6, 25);
	tmp7 = _mm_xor_si128(tmp7, tmp8);
	tmp7 = _mm_xor_si128(tmp7, tmp9);
	// tmp7 = T = (srli(tmp6, 31) ^ srli(tmp6, 30) ^ srli(tmp6, 25))
	tmp8 = _mm_shuffle_epi32(tmp7, 147);

	tmp7 = _mm_and_si128(XMMMASK, tmp8);
	// tmp7 = T >> 96
	tmp8 = _mm_andnot_si128(XMMMASK, tmp8);
	// tmp8 = T << 32

	tmp3 = _mm_xor_si128(tmp3, tmp8);
	// tmp3 = ((T << 32) ^ tmp3)
	tmp6 = _mm_xor_si128(tmp6, tmp7);
	// tmp6 = ((T >> 96) ^ tmp6)

	tmp10 = _mm_slli_epi32(tmp6, 1);
	tmp3 = _mm_xor_si128(tmp3, tmp10);
	tmp11 = _mm_slli_epi32(tmp6, 2);
	tmp3 = _mm_xor_si128(tmp3, tmp11);
	tmp12 = _mm_slli_epi32(tmp6, 7);
	tmp3 = _mm_xor_si128(tmp3, tmp12);

	*res = _mm_xor_si128(tmp3, tmp6);
	// res = ((T << 32) ^ tmp3) ^ \
		slli((T >> 96) ^ tmp6), 1) ^ \
		slli((T >> 96) ^ tmp6), 2) ^ \
		slli((T >> 96) ^ tmp6), 7) ^ \
		((T >> 96) ^ tmp6)             
}
```

因此，我们就实现了使用 intel 指令集在$\mathbb{F}_{2^{128}}$上进行乘法运算的目标。