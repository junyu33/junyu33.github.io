layout: post
title: 陇剑杯入土记
author: junyu33
mathjax: true
categories: 

  - ctf

date: 2021-9-14 20:00:00

---

刚进校不久，我们就被老师鼓励去打首届陇剑杯，当我看到比赛说明的考纲范围时，就发现考察范围与我学习的知识毫无交集。

<!-- more -->

结果让我没想到的是，赛题居然比我想象的还要离谱。比赛时间从上午10点到下午6点，8个小时，我就只做出来3道题，而且分值都不高。

最神奇的是我好不容易找到一个高分值的题目，读取了内存文件，通过网上的工具搞到了系统密码的哈希值，然后死也解不出原文，光这点尝试就花了我两三个小时，在得到答案前的最后一步江郎才尽。

最后成绩出来，yyx1080分，yjp310分，我280分，我又自闭了。只不过战队总分排位838名，总共有3020名，我们占前30%，还是一个尚可的成绩。

# 本队的WriteUp

<img src="ctf01/a.jpg" />

<img src="ctf01/b.jpg" />

<img src="ctf01/c.jpg" />

<img src="ctf01/d.jpg" />

<img src="ctf01/e.jpg" />

<img src="ctf01/f.jpg" />

<img src="ctf01/g.jpg" />

<img src="ctf01/h.jpg" />

<img src="ctf01/i.jpg" />

<img src="ctf01/j.jpg" />

<img src="ctf01/k.jpg" />

<img src="ctf01/l.jpg" />

<img src="ctf01/m.jpg" />

<img src="ctf01/n.jpg" />

<img src="ctf01/o.jpg" />

<img src="ctf01/p.jpg" />

<img src="ctf01/q.jpg" />

# updated on 9，25

今天去看了内存第一题的wp，然后我发现有一份的wp得到哈希值后，就马上把flag搬了出来。~~（原来我与200pts的距离似乎这样近，又似乎那么远......)~~因为那个flag比较长，又不是很正常的单词，用彩虹表基本上不可能。由此我判断：

<img src="ctf01/r.jpg" />

**这个wp一定是假wp，该队肯定跟其他队有py交易！**（想打别人一拳.jpg）

然后我又找到了一个正常的wp，发现**我使用了一模一样的工具，但是却采用了所有的错误方法**，完美绕过了正确答案。

https://www.jianshu.com/p/7c0bea9ff458

<img src="ctf01/s.png" />

<img src="ctf01/t.png" />

<img src="ctf01/u.png" />

此刻我的内心就像这样：

> 比赛时用mimikatz本体**疯狂报错**，麻了。**win10，我的垃圾**
>
> ............



# 彩蛋



>
>比赛前:
>
>宣传！规模！代言！历史上CTF之巅峰！NB!
>
>![img](https://pic2.zhimg.com/50/v2-70227f23029ae7dcbcd09fbb24cbcffa_720w.jpg?source=1940ef5c)![img](https://pic2.zhimg.com/80/v2-70227f23029ae7dcbcd09fbb24cbcffa_720w.jpg?source=1940ef5c)
>
>比赛后:
>
>比赛办的好啊，会办能不能多办点啊，我好多兄弟代打钱还没赚够呢！比赛结束前5分钟11，5分钟后50+是，牛啊牛啊，这比赛怎么会有py是吧，都是企业自己的努力呀！
>
>![img](https://pic1.zhimg.com/50/v2-137ace222ee43a40c2f04d7d2f9b394d_720w.jpg?source=1940ef5c)
>
>这比赛可办的太好啦！我真谢谢你主办方啊，推动了整个ctf圈子的良好习俗之PY(此PY非比PY，自己体会)风气的成长，将PY产业化，更加符合法律法规，建议加大力度，继续保持，直接推动社会经济文化的发展！
>
>另外赛题也令人耳目一新！尤其是里面的选择题！立案深刻，十分符合我国当代社会主义核心价值观！要不是你不说16:00不做，有多少战队要措施错失了明明有全部答案但是不能交的苦恼，真的是民心所望，办比赛办到人民心坎里啦！我替国家和人民谢谢你呀！
>
>https://www.zhihu.com/question/486768971/answer/2120838902