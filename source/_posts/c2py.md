layout: post
title: C转python速成
author: junyu33
mathjax: false
tags: 

- python

categories:

  - 笔记

date: 2022-1-18 23:00:00

---

> 本教程只介绍将python作为一种脚本语言所需要的基本知识点。其目的不是为了机器学习或者数据分析，而是让你写出代码短小、易于维护，而且~~永远也不会爆ull~~的**脚本**。
>
> 具有良好C基础的读者可以在一个下午掌握这些知识点。
>
> 本教程部分引用了[廖雪峰的博客](https://www.liaoxuefeng.com/wiki/1016959663602400)，且以python3为基础。

<!-- more -->

# 与C的主要区别

- 变量定义时不用声明类型，但是是强类型语言

- 句尾没有```;```

- 没有```{}```，而用缩进代替（注意统一使用space或者tab，而且要控制长度统一）

- if、while语句句尾加```:```
- 条件表达式用```and```和```or```，而不是```&&```或```||```

- python的整除是```//```，而不是```/```

- 注释用```#```，而不是```//```

- ```'abc'```和```"abc"```表达的意思相同

# I/O

- 输入一整行并保存：```var = input()```

- 读入带空格的数据：```a, b = map(int, input().split())```

- 读入提示语：```var = input('please type what you want')```

- 输出一行：```print(res)```

- 输出带空格：```print('hello', res1, res2)```

- 格式化输出：```print('my name is %s and I\'m %d year(s) old.' %(name, age))```，或者```print(f'my name is {name} and I\'m {age} year(s) old.')```

- 文件I/O：

```python
with open('D:/tmp1/file.txt','a') as f:
   f.write('this is a trivial test for file I/O.')
with open('D:/tmp1/file.txt') as f:
   content = f.read()
print(content) #然而文件本身有中文时乱码了，「你好」变成了「浣犲ソ」，解决方法在后文。
f.close()
```

# Data type & transfer

变量从创建（赋值）好后，它的类型便确定了。可以通过```type(var)```来查看其类型。

- 整型(int)：```567```，```0xc0ffee```，```2**100+1```，```998244353 // 114514```等。

- 浮点(float)：```3.14```，```1.6e-19```，```0.1 + 0.2```，```math.sqrt(1919810)```等。

- 字符串(str)：```'I\'m \"OK\"!'```，```'\\\t\\'```或者

```python
'''hello,
world!''' #字符串可以换行书写
```

- 字节型(bytes)：如```b'A'```，```b'1qaz2wsx'```。它们不能和int或str做运算。
- 布尔值：```True```和```False```，等同于1和0。它们可以进行算术和逻辑运算，但不能对这两者重新赋值。
- 空值：```None```



- 将字符串转整型：```int(input())```
- 将整型转为浮点：```float(19260817)```
- 16进制转10进制：```int('0xdeadbeef',16)```或```int('0ff1ce'，16)```
- 10进制转2进制：```bin(10)```

# Encoding

（我终于能处理带中文字符的文件了！）

- 几种编码的主要区别（Unicode只用于内存显示，不用于数据储存）：

| 字符 |  ASCII   |      Unicode      |           UTF-8            |
| :--: | :------: | :---------------: | :------------------------: |
|  A   | 01000001 | 00000000 01000001 |          01000001          |
|  中  |    ×     | 01001110 00101101 | 11100100 10111000 10101101 |

- int -> chr用```chr()```，chr -> int用```ord()```

- 将str转成ascii或utf-8需使用```'xxx'.encode('ascii')```或```'xxx'.encode('utf-8')```

- 将字节码转回str则使用decode：

```python
>>> b'ABC'.decode('ascii')
'ABC'
>>> b'\xe4\xb8\xad\xe6\x96\x87'.decode('utf-8')
'中文'
```

回到之前的文件I/O，我们只需要在第二次打开文件时加上一项```encoding = 'utf-8'```即可。

# Basic databases

在python，数据结构被作为*对象*来处理，它们本身已经内置了一些*方法*，这是与面向过程的C的一个重要不同点。

## list——[]

- 创建一个list：```subjects = ['calculus', 'programming', 'politics']```

- 查询最后一项：```subjects[2]```或者```subjects[-1]```

- 对第二项重新赋值：```subjects[1] = PE```或者 ```subjects[-2] = PE```

- 在尾部插入：```subjects.append('introduction_to_computer_system')```

- 在指定位置（下标为2处）插入：```subjects.append(2, 'databases')```

- 在尾部删除：```subjects.pop()```

- 删除下标为3的元素：```subjects.pop(3)```

- 对元素排序（list内元素类型必须相同）：```subjects.sort()```

## tuple——()

- 创建一个tuple：```subjects = ('calculus', 'programming', 'politics')```

tuple**一旦创建，就不能修改**

## dict——{}

（dict类似于c++中的```map```。我本来以为dict也是靠rb-tree实现的，结果一个错误告诉我它是靠hash实现的，因此dict中的元素必须是str、tuple等**不可变对象**，而不能插入list）

- 创建一个dict：```score = {'calculus':96, 'programming':92, 'politics':86}```

- 插入元素：```score['PE']=80```

- 删除元素：```score.pop('calculus')```

## set——set(list)

顾名思义，set中不会含有重复的元素。

- 创建一个set：```academic = set(['programming', 'databases', 'assembly'])```

- 插入元素：```academic.add('networking')```

- 删除元素：```academic.remove('programming')```

- 交集并集：

```python
>>> s1 = set([1, 2, 3])
>>> s2 = set([2, 3, 4])
>>> s1 & s2
{2, 3}
>>> s1 | s2
{1, 2, 3, 4}
```

# Condition and loop

- 再强调一遍：组合条件用```and```和```or```，而不是```&&```或```||```！

条件语句剩下的注意事项看以下例子：

```python
age = int(input())
if age >= 6:
    print('teenager')
elif age >= 18:
    print('adult')
else:
    print('kid')
```

- for循环可以遍历list、tuple和str中的每一个元素：

```python
subjects = ['calculus', 'programming', 'politics']
for i in subjects:
    print(i)
```

- 也可以遍历整数序列（求0~100的整数和）：

```python
sum = 0
for x in range(101):
    sum = sum + x
print(sum)
```

- break和continue依然有效（求0~50的偶数和）：

```python
sum = 0
for x in range(101):
    if x > 50:
        break
    elif x & 1:
        continue
    sum = sum + x
print(sum)
```

- 遍历list、tuple、str中元素更高效的方式是*切片*，切片中的三个参数分别表示初值、终值和步长

```python
>>> L = list(range(100))
>>> L[:10]
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
>>> L[-10:]
[90, 91, 92, 93, 94, 95, 96, 97, 98, 99]
>>> L[10:20]
[10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
>>> L[:10:2]
[0, 2, 4, 6, 8]
>>> L[::5]
[0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95]
>>> L[:]
[0, 1, 2, 3, ..., 99]
>>> L[::-1]
[99, 98, 97, 96, ..., 0]
```


# Function

一个简单的阶乘函数：

```python
def fact(n):
    if n==1:
        return 1
    return n * fact(n - 1)
```

- 函数可以返回多个值——其实是一个tuple

```python
def rot90(x, y):
    tmp = x
    x = -y
    y = tmp
    return x, y
```



## 位置参数

跟你C语言的参数是一个意思。

## 默认参数

比如之前```open```函数的帮助文档是这样写的：

```python
>>> help(open)
Help on built-in function open in module io:

open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None)
    Open file and return a stream.  Raise OSError upon failure.

    file is either a text or byte string giving the name (and the path
    if the file isn't in the current working directory) of the file to
    be opened or an integer file descriptor of the file to be
    wrapped. (If a file descriptor is given, it is closed when the
-- More  --
```

- 除了第一项文件路径之外，剩下的都是默认参数。由于我之前没有填写```encoding```的参数，它默认是```None```，从而导致读取的文件乱码。

> 注意：默认参数需要指向不可变对象！否则每一次函数运行后，得到的结果都可能不同。


# Summary

> The best way to learn a language is to use it.

快去刷题！
