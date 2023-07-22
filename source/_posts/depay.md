layout: post
title: 如何购买 ChatGPT Plus
author: Xfish&junyu33
categories: 

  - 笔记

date: 2023-3-22 13:00:00

---

原文地址：关键词太多，原作者的服务器又备案，所以我就代发了。

<!-- more -->

# ChatGPT虚拟信用卡绑定

## Depay 注册虚拟信用卡

用美区Apple id在手机上下载Depay，然后注册一个账号

注册好之后要先在账号那里（下面的“Me”）进行信息补全和KYC认证，认证是要选中国，填你的真实身份信息，按流程一步步来就好了，审核需要等一小会

还需要在Security那里添加Verification Method，最好是Google verification code，用Authenticator扫描验证就好，每次涉及到支付时都需要验证这个手机令牌

验证都完成后就可以添加一个虚拟信用卡了，在下面的“card”那栏点击Apply card，申请一个mastercard，不是VISA，然后选那个不需要创建费用的基础卡

这样虚拟信用卡就建好了

点CVV可以获得详细信息, cardholder, card number, Expired, CVV等，这些在最后绑定OpenAI是都要用到

## Binance 购买USDT

从 [https://www.binance.com/](https://www.binance.com/) 进入 直接 Continue with Google 

登录后进入要先进行**Verification**，也就是真实的实名认证

所以这里 Residency 选中国，Full Name 写中文即可

Document Type 选 ID Card，也就是中国的身份证

Document Verification 这里电脑摄像头不方便就下一个app就好，需要美区Apple id，用Google登录时需要代理 ，pp里正常操作不需要开代理

后面就是上传照片和人脸验证，验证后应该小等一会就通过了

身份验证好之后，就直接在手机app里购买USDT，点下面四栏中的“交易” → 买币 → 搜索USDT购买就好了，单次最少支付100人民币

如果是通过支付宝的话，它可能直接让你给一个账户转账，这种情况就直接转账就好了，前提支付宝是你的名字。

还有可能是会给你一个产品的链接，单价是1元，你下单了多少钱就买多少个，比如我买100人民币的USDT就下单100个那个商品，然后支付时备注它给的那个名字，支付成功后先点击支付宝上的确认订单，再在Binance里通知卖家发币，上传订单的截图

无论是哪种，都要等待卖家确认，不要直接退出去，收到确认消息后会自动弹出来买入的数额，就成功了

## 转账到信用卡

由于Binance的安全限制，充值购买后需要等24小时才能转账，所以完成上面以后要先等一天

### 获取Recharge address

Depay app上选择下面的“Wallet“ → USDT → Deposit → Choose Network选择BNB Smart Chain(BEP20)，（因为这个比另一个手续费少）

进入后就可以看到一个Recharge address，复制

### Binance提现

Binance app上选择下面的“投资组合” → 提现 → TetherUS，在一个叫发送USDT的表单里，把刚刚复制的粘贴到地址里，转账网路选择跟刚才一样的BNB Smart Chain(BEP20)，输入提现金额，提现&确认订单就可以了

## OpenAI信用卡绑定

需要先准备一个美国的真实地址，最好是免税的州的 Alaska, Delaware, Montana, Oregon 等等都可以，美区Apple id的那个地址就可以

地址的邮编最好要是xxxxx-xxxx这种形式，不要只有前面的数字

[https://platform.openai.com/account/billing/overview](https://platform.openai.com/account/billing/overview) 进入这里 add payment method

**一定要开美国的全局代理**

那个表单里：

- 卡号姓名直接复制粘贴
- 日期 - 两位月份/年份后两位的形式
- CVC就是Depay里查看到的CVV
- 信用卡的邮编只填地址邮编前面的5位
- Country - United States of America
- Address Line 1 - 复制准备好的地址
- Address Line 2 不填
- City, State, Postal Code 复制就好了

Submit!

Successful!!!

# 使用苹果内购开通

> requirements:
>
> - 苹果设备
> - 美国地址生成器：https://www.meiguodizhi.com/usa-address/alaska
> - 双币种信用卡（可选）
> 

鉴于目前有开 ChatGPT Plus 的需求，然而出于IP、虚拟信用卡~~以及失败次数太多~~等多方面的因素，一直没能成功过。

今天偶然看到这篇文章：

> https://zhuanlan.zhihu.com/p/634920483

试了一下，确实成功了，而且相比于上文的方法节省了时间成本（不用等24小时）和金钱成本（手续费少了很多），步骤如下：

1. 注册美区 Apple ID，可以使用大陆手机号验证。
2. 在苹果官网购买礼品卡：https://www.apple.com/shop/buy-giftcard/giftcard （使用支付宝购买也可以，且无需信用卡，本人未尝试）
3. 在你的 App Store 中登录美区 Apple ID 账户并输入礼品卡的激活码 PIN。
4. 下载 Openai，这个时候一般会要求你进一步填一些诸如 first/last name, street, phone number 等信息，按照地址生成器上面填就行。（一般是能过的~
5. 如果没有 shadowrocket，你还需要额外再花 3 刀解决魔法问题，也就是你的礼品卡面值至少是 23 刀。
6. 解决问题之后登录进去，再开通 Plus 应该就没有问题了。这个 Plus 的服务是苹果设备和网页都互通的，包括历史记录。

~~所以说，苹果就是神~~