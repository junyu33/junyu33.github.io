layout: post 
title: 博客的第二次维护
author: junyu33 
mathjax: true 
categories: 

  - test

date: 2023-1-30 10:00:00

---

由于 win 这边 node 版本过高，导致 hexo 无法部署博客，昨天花了一下午时间维护了一下博客。

上次维护是为了部署 twikoo 评论区，将 nexT 版本从7升级到了 8.1.0，好像挺折腾的，弄了不少时间。

只能说经过了许多次配环境的考验，效率比以前提高了不少。

<!-- more -->

# Steps

- update hexo from 5.2.0 -> 6.3.0 
- update nexT from 8.1.0 -> 8.14.1
- update twikoo from 1.5.x -> 1.6.8

其实这三件事情并没有解决**无法部署博客**这个根本问题，而网上的一堆博客都是齐刷刷地要降级 node 至版本 12 以下，这种开历史倒车的行为我怎么能忍？于是我在[这个链接](https://github.com/hexojs/hexo/issues/4281)找到了最终方案。

> [@WinterSoHot](https://github.com/WinterSoHot)
> It seems caused by [hexo-fs](https://github.com/hexojs/hexo-deployer-git/blame/c312a1507a8136ca6bba23949cbf7bba55d739d7/package.json#L41). hexo-deployer-git depends on hexo-fs and hexo-fs@2.0.0 is incompatible with Node.js 14.
>
> We are already released `hexo-fs@2.0.1` that supports Node.js 14.
> Would you please re-install `hexo-deployer-git`?
>
> I think, after re-install `hexo d` will work well.

# Changes

当然，这么折腾也还是带来了一些好处的，比如：

- 似乎解决了$\LaTeX$在 Typora 的显示跟网页 MathJax 不一致的问题。
- 博客的字数统计增加了大约 5.5%。

以及一些无伤大雅的变化：

- 友链和 TOC、站点浏览整合到了一起。
- 博客首页的 Header 粉色区域变窄了一些。

——虽然也带来了一些损失：

- 清空了本来就冷寂的评论区的评论记录。

# Tests

> 节选自《（已完结）概统笔记》的**区间估计（背）**章节。

估计$\mu$的$(1-\alpha)$的置信区间。

> `估计$\mu$的$(1-\alpha)$的置信区间。`

若$\sigma^2$已知，则为$(\overline{X}-\frac{\sigma}{\sqrt{n}}u_{1-\frac{\alpha}{2}}, \overline{X}+\frac{\sigma}{\sqrt{n}}u_{1-\frac{\alpha}{2}})$

> `若$\sigma^2$已知，则为$(\overline{X}-\frac{\sigma}{\sqrt{n}}u_{1-\frac{\alpha}{2}}, \overline{X}+\frac{\sigma}{\sqrt{n}}u_{1-\frac{\alpha}{2}})$`

若$\sigma^2$未知，则为$(\overline{X}-\frac{S}{\sqrt{n}}t_{1-\frac{\alpha}{2}}(n-1), \overline{X}+\frac{S}{\sqrt{n}}u_{1-\frac{\alpha}{2}}(n-1))$

> `若$\sigma^2$未知，则为$(\overline{X}-\frac{S}{\sqrt{n}}t_{1-\frac{\alpha}{2}}(n-1), \overline{X}+\frac{S}{\sqrt{n}}u_{1-\frac{\alpha}{2}}(n-1))$`

估计$\sigma^2$的$(1-\alpha)$的置信区间。

> `估计$\sigma^2$的$(1-\alpha)$的置信区间。`

$(\frac{(n-1)s^2}{\chi^2_{1-\frac{\alpha}{2}}(n-1)}, \frac{(n-1)s^2}{\chi^2_\frac{\alpha}{2}(n-1)})$

> `$(\frac{(n-1)s^2}{\chi^2_{1-\frac{\alpha}{2}}(n-1)},\frac{(n-1)s^2}{\chi^2_\frac{\alpha}{2}(n-1)})$`

> 看来`\overline{X}`这个bug确实被修复了，并且打行间公式用一个`$`也不会出现渲染失败的问题。