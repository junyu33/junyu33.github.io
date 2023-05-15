layout: post
title: （不定期更新）nju-pa 心得
author: junyu33
mathjax: true
categories: 

  - develop

tags:

  - c
  - linux

date: 2023-5-13 12:30:00

---

TODO: 其它专业课有思路再写。

<!-- more -->

# 背景（个人吐槽，可skip）

鉴于本校的专业课并不能让我学到多少东西，我开始思索自己与非科班的同学的技术水平是否还存在着区别（抑或是他们可能已经通过报班的方式已经超越了我们？例如`Java`），而我自己的优势又在哪里。

回想起一年前秦院对我说过，从用人单位的角度来看，本院的学子的编程水平不如隔壁电科。当时我还对这句话半信半疑，但从现在的课程设计角度来看，这的确是不争的事实（或者说是必然的结果）。学院也确实作出了一些改进，比如说`C`的在线OJ（只不过因为较为 aggressive 与排版问题饱受诟病），当然这还远远不够。

从提升个人能力的角度来看，留给我的时间已经不多了，我必须摒弃一切与这个目标相悖的杂事（按优先级看依次是综测、大创、各种竞赛（包括低质量的 CTF ），最后是 GPA（自己的优势有时也是弱点）），以给自己留出尽可能多的时间来学习真正与我的方向相关的，或者是 fundamental 的东西（比如说 OS —— by `lotus`）。

关于 OS 这门课，学院的理论课只能说不算差，以应试为主。与此相比，实验课就处在一个十分尴尬的地位，具体理由如下：

- 没有先导课程：缺少对 `linux` 基础的讲授和 `git` 的使用教程，这些东西在我完成 `nachOS` 实验的过程中极大地提升了工作效率。为什么这么说呢，因为肯定有同学还是在通过注释之前几个 lab 代码的方式（或者重新 copy 原始的 source ）来写当前 lab 的代码，懂的都懂。
- 过分降低了难度：目前 OS 实验课的方式是结合了 PPT 讲义与演示视频的形式，其中演示视频不可避免的会展示一些 `source code`，而同学用手机拍摄/录制这段内容是无法避免的，从而实验的难度降格为在不同的 source 中补全部分代码，我们便丧失了 `RTFSC` 的能力。这样做的后果就是：轻则不理解 `nachOS` 的整体架构，重则无法回答梁刚老师在 `lab8` 提出的那几个稍微 `RTFSC` 就能回答的问题。
- 抄袭问题严重：人都是有惰性的，`nachOS` 是一个陈旧的项目，其中许多 lab 的答案随便一搜就能找到，我其实也抄过。

# why do I want to be a masochist (by doing PA)

~~simple, because I enjoy this~~

- Being introduced by `Tiger1218`, `nju_pa` is absolutely a great course. In compare with `nand2tetris` I previously finished, it is more hard-core but a more smooth learning curve.

- I have no more time, I need to acquire more information in a rather short period of time. High information density means high difficulty. Therefore, keeping in touch with something challenging is unavoidable.

- In academia, having a deeper understanding of ISA & OS benefits to further research. In engineering, praticing coding skills makes me more competent in both major or non-major students in CS field.

# pa0

I've already used Linux and built workflow for some time. So I just installed `neovim` and clone the source.

Learned some useful git commands like `git branch`, `git checkout`.

[The Missing Semester of Your CS Education](https://missing.csail.mit.edu/) is a good course, bookmarked.

# pa1

## 1.1

At first I was dumbfounded. Copilot gives some code suggestions, which makes me quickly understand what I need to do. Actually, it is quite easy.

## 1.2

Several months ago I learned regex and I forgot it. It took me 30min to learn it again. Actually the `tokenize` step is much easier than compiler section of `nand2tetris`.

Copilot helped me quickly finished the structure of `eval` function, but it made a mistake when finding the dominant operator and I spent several hours debugging this.

When it comes to modifying `sdb.c` to test a batch of expressions. I mistyped the path to my input file (btw, copilot suggested the path of `yzh`'s project, which is a privacy issue). At first I don't know I can enable debug info in `menuconfig`, and `static` functions increased the difficulty analyzing the assembly instructions when using `gdb`. Therefore, it took me nearly an hour to debug this.

Also, I had a hard time tackling the floating point exception (div by 0) in expression generator. My idea is compile and run it, while redirecting exceptions to stderr. If `grep exception stderr_file` doesn't return `0`, we think the expression is valid. However there are still some exceptions printed in my `stdout_file`, finally I've to use another command to filter the output.

```bash
perl -pe 's/Floating\ point\ exception\n//g' stdout_file > final_input
```

## 1.3

Expanding the `eval` function is not very hard, one important point is to change a condition to tackle unary operator (like `*` and `-`).

Implementing watchpoint pool is just some basic linklist operations, copilot did a good job.

However, copilot made a big mistake implementing watchpoint itself, it messed the return value of `check_wp`. I spent several hours again debugging this.