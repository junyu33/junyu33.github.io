

layout: post

title: bandit通关记录

author: junyu33

mathjax: true

tags: 

- linux

categories: 

- 笔记

date: 2022-4-1 17:00:00

---

一个练习Linux基础命令的网站，属于overthewire.org关卡系列中的基础部分。

本文中的level指的是网站的guide`level n -> level (n+1)`中的后者。

网站链接：https://overthewire.org/wargames/bandit/

<!-- more -->

# level1、level14

## SSH的使用

>你无法回忆起你学过的任何算法或者 OI 知识。你无法回忆起一切。你无法回忆起你叫什么名字。
>
>你能回忆起…… $49233121176$，或者再具体一点是 $\frac{49.233121176}{22}$。你能回忆起第 $22$ 号港口通往三山海。三山海是你向往的目的地，你一定要到达这里。

考察了ssh的基本使用：

网站说了用户名和密码都是bandit0

```shell
ssh bandit0@bandit.labs.overthewire.org -p 2220
```

如果只有密钥，没有密码的话：

```bash
ssh bandit14@bandit.labs.overthewire.org -p 2220 -i ./bandit14.sshkey
```

# level2~level5

## 基本的路径跳转和文件查看

`ls -a`查看隐藏文件。

`ls -l`查看文件的详细信息，包括权限、属于的用户和组、 文件大小、修改时间等等。

`cd ../`返回上一级。

`cd '<dir>'`可以跳转到包含空格或者特殊字符（比如`-`）的路径。

# level6、level7

## 按照大小查找文件

```bash
find -size 1033c
```

查找大小为1033字节的文件。

```bash
find -size +5k -size -99k
```

查找大小基于5k~99k的文件。

常用的储存单位为`c`,`k`,`M`,和`G`.不要问我为什么前两个小写，后两个大写。

## 按照用户和组查找文件

与上文类似：`-user`,`-group`.

# level8、level9、level18

## 查找指定字串

```bash
grep millionth < data.txt
```

其中`<`是文件输入流，类似也有`>`作为输出流。

## 查找文本中唯一出现的字串

```bash
sort data.txt | uniq -c
```

其中`sort`会将文本中的字符串按照字典序排序。

`|`是管道符，用来将前一个命令的输出作为后一个命令的输入。

uniq是文本去重命令，它会将文本中重复出现的行压缩至一行。而`-c`参数的含义是显示该串重复出现的次数，这样我们就可以方便找到那个只出现一次的串。

## 文件比较

```bash
diff <dir_1> <dir_2>
```



# level10~level12

## 编码的考察

举了ascii，base64和rot13。

其实不一定要使用Linux内置的命令，上网找在线转换器或者编写脚本都是可以的。

# level13

> 13果然不是一个好数字。正如这道题的解题过程一样令人恶心。

## 16进制文本与二进制文件的转换

`xxd`将二进制文件转换为16进制文本。

`xxd -r`逆向操作。

## 复制、移动文件和重命名

这关需要对文件进行操作，受权限限制，需要将文件移动到临时目录。

`cp <src_dir> <dst_dir>`将文件从原路径复制到目的路径。

`mv <src_dir> <dst_dir>`将文件从原路径移动到目的路径。

重命名可以通过`mv <old_name> <new_name>`来实现。

## 文件类型判断

使用file命令即可，不会受扩展名影响。

因为Linux本身就没有“扩展名”这种说法，所谓的“扩展名”是为了方便人类识别才有的。

## 解压文件

### gunzip

解压：首先确保其后缀为`.gz`，解压命令为：`gzip -d <filename>`

压缩：`gzip <filename>`

### bzip2

解压：`bzip2 -d <filename>`

压缩：`bzip2 <filename>`

### tar

解压：`tar -xvf <filename>`

打包：`tar -cvf <dst_name> <src_name>`，建议`<dst_name>`以`tar`作为后缀。

使用`gzip`压缩：`tar -zcvf <dst_name> <src_name>`，建议`<dst_name>`以`tar.gz`或`tgz`作为后缀。

使用`bzip2`压缩：`tar -jcvf <dst_name> <src_name>`，建议`<dst_name>`以`bz2`作为后缀。

# level15~level17

> 网络部分我是一窍不通。

## nc连接某个地址并发送数据。

```bash
echo <your text> | nc localhost 30000
```

其中`localhost`即本地`127.0.0.1`，而`30000`是端口号。

## telnet连接某个地址并发送数据

```bash
telnet localhost 30000
#之后你可以输入数据并回车，以进行发送
```

## ssl连接某个地址并发送加密数据

```bash
openssl s_client -ign_eof -connect localhost:30001
#之后你可以输入数据并回车，以进行发送
#ps: 似乎 -ign_eof 这个参数不是必须的
```

## nmap扫描端口

```bash
nmap -p 31000-32000 localhost
```

在31000~32000端口扫描活动的端口。

~~平时不要乱扫，小心进局子~~

# bandit19~bandit21

> 总之，这几关让我运行了一些奇奇怪怪的程序。

## 从自动退出的终端中运行命令

```bash
ssh bandit18@bandit.labs.overthewire.org -p 2220 cat readme
```

## linux执行后台命令

```bash
cat /etc/bandit_pass/bandit20 | nc -l 50000 &
```

其中`&`表示让命令在后台运行，这样当你之后`nc`到`50000`这个端口时，就会自动返回这个pass。

# bandit22~bandit24

cron相当于windows的任务计划程序。

只不过这几关不是让你创建计划任务，而是让你读别人脚本和自己写一个脚本。

~~第二十四关的权限过滤不是很严格，我不仅看到了别人的脚本，还`rm -rf`了一部分。目测玩过这个游戏的不超过100个人？~~

记得脚本第一行要写`#!/bin/bash`

# level25

## brute-forcing

其实我是用c脚本生成一万行指令，轰炸进去。如果密码正确连接会中断。

我们可以大致确定密码的范围，然后缩减指令行数，重新轰炸。

这个时候，再翻一翻前面的爆破记录，应该能看到密码。



当然，优雅的做法是——python脚本（网上抄的）。

```python
#!/usr/bin/python
from pwn import *
from multiprocessing import Process

def brute(nrOne,nrTwo):
    for pin in range(nrOne,nrTwo):
        pin = str(pin).zfill(4)

        r = remote('127.0.0.1', 30002)
        r.recv()
        r.send('UoMYxxxxxxxxxxxxxxxxxxxxxxxxxxxx ' + pin + '\n')

        if 'Wrong' not in r.recvline():
            print '[+] Successful -> ' + pin
            print r.recvline()
            r.close()
        else:
            if int(pin) % 100 == 0:
                print '[!] Failed -> ' + pin
            r.close()

if __name__=='__main__':
    p1 = Process(target = brute, args = (0,2500,))
    p2 = Process(target = brute, args = (2500,5000,))
    p3 = Process(target = brute, args = (5000,7500,))
    p4 = Process(target = brute, args = (7500,10000,))
    p1.start()
    p2.start()
    p3.start()
    p4.start()

```

# level26、level27

> 令人脑洞大开的两关。

## 查看系统使用了什么终端

只需`cat /etc/passwd`即可，最后一个就是默认终端。

## 如何从showtext程序进入vim

将终端的窗口缩小，使文件显示不完，这个时候会有一个`more`的提示，敲`v`即可进入vim。

## 如何使用vim修改终端并进入bash

在vim的命令模式中输入以下两行：

`:set shell=/bin/bash`

`:shell`

# level28~level32

## git的各种操作

克隆：`git clone <git_address>`

拉取：`git pull`

上传：

```bash
git add .
git commit -m "<your_description>"
git push origin master
```



回退一步：`git reset --hard HEAD^`

查看历史版本：`git log --pretty=oneline`

回退到指定版本：`git reset <commit_id>`



查看分支：`git branch -a`

选择分支：`git checkout <branch>`



查看标签：`git tag`

创建标签：`git tag -a v1.4 -m 'my version 1.4'`.其中`-a`是“带附注”的意思。

# level33

> 一个将小写字母自动转成大写的SHELL——也就是看上去什么也运行不了。
>
> 但是输个$0就进入正常的shell了，特别迷。
>
> 能解释的发下评论区。

## 介绍 \\$0、\\$1、\\$2、\\$#、\\$@、\\$*、\\$? 的含义

参见：https://segmentfault.com/a/1190000021435389
