

layout: post

title: （不定期更新）数据库学习笔记

author: junyu33

tags: 

categories: 

- 笔记

date: 2022-3-25 12:00:00

---

数据库其实不难学，就是头有点凉。

<!-- more -->

# 概念逻辑转化规律——week5

重点——**relationship**

## 1.*

### S-S

<img src="database/1.png">

<img src="database/2.png">

主关键字做了外部关键字

1的主关键字移向了n

#### 有属性

**如果有属性，属性去掉后基数交换，再依照上述规则处理**

> 概念模型建模的时候注意：先画概念模型的1*

### S-W

<img src="database/3.png">

弱实体没有主关键字，不能移向强实体

<img src="database/4.png">

> 1：\* 二元 S——W
> 1——>\* 主关键字——>主关键字+外部关键字
>
> from our teacher

#### 有属性

<img src="database/5.png">

括号表示preference是弱实体。

**此时生成逻辑模型出错**

<img src="database/6.png">

把关系的属性移入依赖的弱实体

(这里的Relationship_2应是state，而preference中的state项应为Date项)

<img src='database/7.png'>

再依照之前的规律转换

## 1.1

### S-S

<img src='database/8.png'>

双方强制参与会报警，根据业务将其中一方改为0-1
