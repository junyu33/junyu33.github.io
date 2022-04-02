layout: post
title: 游戏项目之简易扫雷
author: junyu33
mathjax: false
tags: 

- c++

categories:

  - develop

date: 2021-12-28 10:30:00

---

本项目是程序设计课程中的游戏项目。

github链接：https://github.com/junyu33/MineSweep/

欢迎大家提issue和pull request

<!-- more -->

# 简要介绍

1）本项目是一个基于EGE图形库的扫雷游戏。

2）本项目的功能说明：

   ①简单、普通、困难、自定义四种模式

   ②前三种模式的时间排行榜（文件归档）

   ③快速扫雷与快速插旗

   ④同时支持鼠标和键盘操作

   ⑤游戏背景音乐的播放和控制 

3）本项目的开发环境和工具

   开发环境：vscode mingw 8.1.0

   工具：ege20.08

## 游戏截图

[<img src="https://s4.ax1x.com/2021/12/20/TnFiAe.png" alt="TnFiAe.png" style="zoom: 67%;" />](https://imgtu.com/i/TnFiAe)

# Changelog

```
1.0
(source code)
2.0
configuration interface (ok)
mine-generating xp->win7 mode (ok)
basic keyboard support (ok)
2.1
timing (ok)
minecnt (ok)
2.2
winning interface with personal things (ok)
fast-sweeping keyboard support (ok)
highlight numbers (ok)
small changes about lastx,lasty (ok)
3.0
leaderboard (ok)
three modes (ok)
3.1
quit in menu (ok)
add fast-flaggging (keyboard only) (ok)
lowlight blanks (keyboard only) (ok)
3.2
add colors to numbers (ok)
random block to start (ok)
```

# 模块划分

[![TrfvL9.png](https://s4.ax1x.com/2021/12/28/TrfvL9.png)](https://imgtu.com/i/TrfvL9)

# 函数调用关系

[![TrfzZR.png](https://s4.ax1x.com/2021/12/28/TrfzZR.png)](https://imgtu.com/i/TrfzZR)
