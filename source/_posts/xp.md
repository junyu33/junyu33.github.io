layout: post
title: Xposed——从入门到放弃
author: junyu33
categories: 

  - develop


tags:

  - linux
  - android

date: 2021-8-10 23:00:00

---

换新手机后，经过两天的不屑努力（与50元解bootloader锁的智商税？）我终于让华为的手机成了我的手机。

<!-- more -->

<img src="xp/1.png" style="zoom: 33%;" />

目前还没发现有什么特别的用处，等以后**有技术了**再来填坑。

## updated on 2024-8-17

这段时间比较空闲，于是我终于有时间来填坑了。

首先我要说的是，我感觉 root 后能做的事情比我想象得少很多。毕竟这个手机的安卓版本是 7.0，已经被时代给抛弃了。

以下的事情有些不用 root 也能搞定，但比较 hack 的操作我也会写在下面。

### 卸载系统应用（成功）

首先使用 [MyAndroidTools](https://www.myandroidtools.com/) 并不能正常卸载（即使拿到了 root 权限），原因未知。

正确的做法是拿到包名后使用 root 权限进入 shell，然后键入以下命令：

```sh
adb shell pm uninstall --user 0 <package_name>
```

笔者通过对比 MyAndroidTools 前后应用的列表差别，确认这个是永久卸载，而不是高版本 Android 只在当前用户删除。

### System RW（失败）

笔者在新国大坐牢，曾经在 Ubuntu 笔记本搞 Waydroid 的时候，意外地发现了 SystemRW （www.systemrw.com，不用点，已经挂了）这个工具。我曾使用这个工具成功使我的 Waydroid 的 system 分区可写，从而有了愉快的网络抓包经历。

如今，这个工具的官网已经挂了，但它的解压文件还乖乖躺在了我的电脑里。于是我熟练的将它 push 到了手机上，然后运行了它。结果如下：

```sh
HWSTF:/data/local/tmp/sysrw_1.41 # ./sysrw

 ---------------------------------------------------
|  Welcome to the one and only original, universal  |
|===================================================|
|        SystemRW / SuperRW v1.41 featuring         |
|          MakeRW / ro2rw v1.1 by lebigmac          |
|===================================================|
|(read-only-2-read/write SUPER partition converter) |
|---------------------------------------------------|
|Also known as System-RW/Vendor-RW/Product-RW/Odm-RW|
|   FORCE-RW, TRUE-RW, EROFS-RW, F2FS-RW, EXT4-RW,  |
| THE REAL RW, FULL-RW, ERWFS, F2FS-2-RW-CONVERTER, |
|EROFS-2-RW-CONVERTER, Super Flasher/Resizer/Patcher|
| Root enhancer, Full Root, Real Root & more aliases|
|---------------------------------------------------|
|Inspiring a whole generation of talented developers|
|     and empowering the open source community.     |
|     The prophecy has finally been fullfilled!     |
|The Pandora's Box has been fully unlocked at last! |
|Let the Olympic System Modding Games (OASMG) begin!|
| The power is now in YOUR hands! And do not forget:|
|    With great power comes great responsibility!   |
|---------------------------------------------------|
|  CREDITS: @lebigmac @Brepro1 @Kolibass @Yuki1001  |
| Shoutouts: harpreet.s, frxhb, HemanthJabalpuri    |
|===================================================|
|    OFFICIAL HOMEPAGE @ http://www.systemrw.com    |
|===================================================|
|You can use this software for free for educational,|
| personal, non-commercial, legal purposes. To use  |
|this software for commercial purposes,please rent a|
| commercial usage license @ the official link above|
|---------------------------------------------------|
|   WARNING! NEVER TRUST THE SOFTWARE OF THIEVES!   |
|This project (or parts thereof) was stolen, hacked |
|    and/or abused by brigudav, leegarchat & co!    |
|dr-ketan steal my unique System-RW name from me :( |
|---------------------------------------------------|
|Always download original System-RW from link above!|
|---------------------------------------------------|
|You can learn from my code but please do not steal,|
| hack, crack or abuse it in any way! Thank you! <3 |
 ---------------------------------------------------
sysrw: Custom exclude detected: " odm product system_dlkm system_ext vendor vendor_dlkm "
sysrw: Backups enabled
sysrw: Initiating procedure...

sysrw: Device is in Android mode
sysrw: Current device: HUAWEI 
sysrw: Current device architecture: aarch64
sysrw: Please install Android 10 or newer and try again
```

> 这个 developer 还是有点中二的，你说对不对？

很不幸，这个工具只支持 Android 10 以上的版本。我之前也尝试进 fastboot 模式刷了一个 Android 13 的 ROM，但是这个 ROM 有点问题，导致我无法进入系统。所以这个方法暂时不可行。

### 尝试将 magisk root 方法换成 kernelSU（失败）

显然，我认为 kernelSU 是一个更加 advanced 的 root 方法。或许可以解决 /system 分区不可写的问题。

然而：

> KernelSU officially supports Android GKI 2.0 devices (kernel 5.10+). Older kernels (4.14+) are also compatible, but the kernel will have to be built manually.

```sh
HWSTF:/ # uname -a
Linux localhost 4.1.18-g7bd0d96 #1 SMP PREEMPT Fri Oct 12 10:15:13 CST 2018 aarch64
```

显然，我的手机的内核版本是 4.1.18，所以这个方法也不可行。

### 将我的 shizuku 更换为 sui（失败）

shizuku 在它的应用里说 sui 将最终取代 shizuku，于是我尝试安装 sui。

但是，我试了 github 诸多版本的 sui（zygisk），它们的安装包在我的的手机上都无法解析。个人猜测应该是 Android 版本问题。只好作罢。

### 安装 Ubuntu（成功）

最理想的情况是直接裸机安装 Ubuntu，但据 misane 的说法，ubuntu touch 支持的手机型号很少。另外，手机的驱动是闭源的，而且不一定在 Linux 内核层，有可能在安卓 HAL 层，所以就难办。

于是我只好退而求其次，在 Termux 上安装 Ubuntu。最新版的 Termux 在我的设备上无法安装，我找到的可用于 7.0 的版本是 0.88。

然后，我参照[这个教程](https://blog.csdn.net/xyzAriel/article/details/104698491)在 Termux 上配置好环境并安装了 Ubuntu，其实感觉功能并不比 Termux 本身强多少。

```sh
apt-get update
apt-get upgrade -y
apt-get install wget proot git -y
termux-setup-storage
git clone https://github.com/MFDGaming/ubuntu-in-termux.git
cd ubuntu-in-termux
chmod +x ubuntu.sh
./ubuntu.sh -y
# start
./startubuntu.sh
```

> 另外这里的清华源地址有错，正确的 Termux 源是 `deb https://mirrors.tuna.tsinghua.edu.cn/termux/apt/termux-main stable main`。
>
> 另外，安装也不需要几个小时，开了代理，最多一分钟。

BTW，用手机敲命令真的很难受，于是我在手机上装了个 openssh，从电脑端来操作。

> 这里启动 sshd 服务不需要 systemctl 那一套，直接 `sshd` 就行。

### 防止杀后台（成功）

我问了下 ChatGPT，他推荐了 App Systemizer，看了下 GitHub，这个工具最后一次更新还是7年前，支持 Magisk v14（我的版本是 27）。GitHub 没有提供安装包，而 Magisk 目前也不提供搜索模块的功能。于是我只能去 [XDA](https://xdaforums.com/t/module-terminal-app-systemizer-v17-3-1.3585851/) 找到最新版本的压缩包（2019年），往 Magisk 里一丢，安装成功。

至于 Magisk 怎么安装离线 zip 包，这里简单讲一下：模块 -> 从本地安装 -> 选择 RE/MT 文件管理器 -> 选择 zip 包即可。至于使用方法参考 XDA 链接里的 youtube 视频即可。

另外，我也可以通过使屏幕保持常亮来防止后台被杀，但因为未知原因，设置里面的休眠选项是灰色的，无法更改。根据 ChatGPT 的回答，它说你可以使用 ADB 或 root 权限直接修改安卓系统的 settings 数据库，来调整休眠时间。具体命令如下：

```sh
adb shell settings put system screen_off_timeout 2147483647
```

我试了下，确实管用。设置这边这个值变成“永不”了。于是，这个旧手机离变成树莓派已经不远了。

### hack 系统主题（成功）

我觉得我旧手机的系统主题挺好看的，想迁移到自己现在的主力机上。我在旧手机的主题商店得知这个主题的名字叫“再见时光”，然后在主力机上一搜，找不到这个主题。

于是我参考了[这个链接](https://www.bilibili.com/video/av340138233/)得知华为的主题包后缀名是`hwt`，但路径与视频中的不同，于是我选择：

```sh
find / -name "*.hwt" 2>/dev/null
```

部分输出如下：

```
./system/emui/china/themes/Droidsansfallback.hwt                                              
./system/emui/china/themes/FZLT.hwt                                                           
./system/emui/china/themes/FZLTH.hwt                                                          
./storage/emulated/0/HWThemes/.cache/Rhapsody.hwt                                             
./storage/emulated/0/HWThemes/.cache/Flow.hwt                                                 
./storage/emulated/0/HWThemes/.cache/Memento.hwt                                              
./storage/emulated/0/HWThemes/.cache/Serenade.hwt                                             
./storage/emulated/0/HWThemes/.cache/Symphony.hwt                                             
./storage/emulated/0/HWThemes/.cache/Waltz.hwt                                                
./storage/emulated/0/HWThemes/.cache/Droidsansfallback.hwt                                    
./storage/emulated/0/HWThemes/.cache/FZLT.hwt                                                 
./storage/emulated/0/HWThemes/.cache/FZLTH.hwt                                                
./storage/emulated/0/HWThemes/.cache/cover/onlinethemepreview/73E071837FEE1E3023D3BE4E1C725237.hwt
./storage/emulated/0/HWThemes/.cache/cover/onlinethemepreview/b7e06a7ad1d2468082d4bcf11f1d158f.hwt
./storage/emulated/0/HWThemes/.cache/cover/onlinethemepreview/20170322172846.62772498.hwt     
./storage/emulated/0/HWThemes/.cache/cover/onlinethemepreview/20170331163957.18140689.hwt     
./storage/emulated/0/HWThemes/.cache/cover/onlinethemepreview/628834ba702c488ebde3a43777795a7d.hwt
./storage/emulated/0/HWThemes/.cache/cover/onlinethemepreview/1FCE0D891DD45D68F7E67399E1499281.hwt
./storage/emulated/0/HWThemes/.cache/cover/onlinethemepreview/CF0193A7174829B27F8D8465E3231170.hwt
./storage/emulated/0/HWThemes/.cache/20170331163957.18140689.hwt                               
./storage/emulated/0/HWThemes/.cache/b7e06a7ad1d2468082d4bcf11f1d158f.hwt                     
./storage/emulated/0/HWThemes/.cache/628834ba702c488ebde3a43777795a7d.hwt                      
./storage/emulated/0/HWThemes/20170331163957.18140689.hwt                                     
./storage/emulated/0/HWThemes/b7e06a7ad1d2468082d4bcf11f1d158f.hwt                             
./storage/emulated/0/HWThemes/628834ba702c488ebde3a43777795a7d.hwt
```

于是主题的路径是`/storage/emulated/0/HWThemes`，然后查看`.cache`目录，ls 一下：

```sh
HWSTF:/storage/emulated/0/HWThemes/.cache # ls
20170331163957.18140689.hwt          Flow.hwt     Waltz.hwt                            
628834ba702c488ebde3a43777795a7d.hwt Memento.hwt  b7e06a7ad1d2468082d4bcf11f1d158f.hwt 
Droidsansfallback.hwt                Rhapsody.hwt cover                                
FZLT.hwt                             Serenade.hwt diycache                             
FZLTH.hwt                            Symphony.hwt themecache
```

这里面每一个都是文件夹，内部都有一个名为`description.xml`的文件，查看这个文件就可以得知主题的名称，例如：

```sh
HWSTF:/storage/emulated/0/HWThemes/.cache # cat b7e06a7ad1d2468082d4bcf11f1d158f.hwt/description.xml
<?xml version="1.0" encoding="UTF-8"?>

<HwTheme>
    <title>bye lyh</title>
    <title-cn>再见时光</title-cn>
    <author>云海</author>
    <designer>云海</designer>
    <screen>FHD</screen>
    <version>5.0.0</version>
    <font>Default</font>
    <font-cn>默认</font-cn>
    <briefinfo>【限时免费】需要壁纸的请加微信公众号：YHtheme 回复 壁纸下载 ，或加QQ100750086，备注华为主题
锁屏是动态锁屏，会有花瓣树叶等飘落，已适配海量图标，拨号界面，联系人，短信列表等界面。
</briefinfo>
</HwTheme>




HWSTF:/storage/emulated/0/HWThemes/.cache # 
```

于是我们得知，应该将 `b7e06a7ad1d2468082d4bcf11f1d158f.hwt` 这个文件夹 pull 出来，这就算成功一半了。

接着，我应该将`HWThemes`目录的这个`hwt`文件拷贝到主力机上，自然，路径跟旧手机肯定又不一样。我们知道，此时的华为主题商店已经变成了荣耀主题商店，于是对应的路径是`/storage/emulated/0/Honor/Themes`，里面有`themecache`这个文件夹，因此可以基本确定把`hwt`文件放在这个路径下就可以了。

我如法炮制，打开主力机的荣耀主题商店，“我的主题”里面果然就有了这个，甚至还能看这个主题的用户评论。

> 看来华为荣耀还是没有彻底分家啊。

可能是因为屏幕长宽比不同，这个主题适配到主力机上锁屏界面有点瑕疵，短信界面也无法显示背景。但除此之外还是挺完美的。

### 绿色守护（成功）

针对 Android 7 能用的旧版本绿色守护是在[这里](http://shouyou.kuai8.com/game/60585.html)找到的。我启用了 root 功能，但工作模式中的 Xposed 模式不能选择，原因未知。

出于隐私保护，我休眠了除 NCalc+ 和 termux 外所有的联网应用，除此之外我没有做其他操作。

### frida 初探（成功）

首先我在 GitHub 上找到了 magisk-frida，在 Xposed 安装了 zip 包。然后在我的 Ubuntu 主机配置 frida client，步骤如下：

```sh
conda create -n frida python=3.11
conda activate frida
pip3 install frida frida-tools
```

然后运行：

```sh
adb forward tcp:27042 tcp:27042
frida-ps -U
```

可以看到手机上的进程。

```sh
  PID  Name
-----  ------------------------------------------
12346  Clash Meta for Android
 1575  Gboard
19507  Google Play 商店
  498  HwCamCfgSvr
  509  HwServiceHost
16389  Magisk
12938  MyAndroidTools
 1932  SIM 卡应用
18117  Via
12080  adbd
 2256  android.process.acore
12014  android.process.media
  552  audioserver
  485  bastetd
  500  cameraserver
  516  chargemonitor
 1570  com.android.bluetooth
19319  com.android.defcontainer
 2588  com.android.incallui
 2748  com.android.nfc
19294  com.android.packageinstaller
19231  com.android.providers.calendar
19681  com.android.vending:background
 6247  com.bidau.nkngl
18285  com.github.metacubex.clash.meta
 2523  com.google.android.ext.services
 2637  com.google.android.gms
 2292  com.google.android.gms.persistent
11716  com.google.android.gms.unstable
19209  com.google.android.webview:webview_service
11682  com.google.process.gapps
 1910  com.huawei.android.chr
 2190  com.huawei.android.instantshare
 2830  com.huawei.android.launcher
 6480  com.huawei.android.pushagent.PushService
 2652  com.huawei.bd
...
```

#### com.bidau.nkngl

这里有一个叫`com.bidau.nkngl`的进程，我觉得这个进程很可疑，通过手机的 MyAndroidTools 得知这个应用的名字叫`SystemStars`，Apk路径为`/system/app/MTExMSxodW/MTExMSxodWF3ZWktc3RmLWFsMDAsNjU1OTUsMQ==.apk`，base64解一下得到`1111,hu/1111,huawei-stf-al00,65595,1`，感觉没什么意思。于是我又决定用 frida 来看看这个应用的行为，具体的我还是查看与网络相关的行为：

首先枚举与网络相关的类：

```javascript
Java.perform(function() {
    Java.enumerateLoadedClasses({
        onMatch: function(className) {
            if (className.includes("okhttp") || className.includes("http") || className.includes("network")) {
                console.log("Loaded class: " + className);
            }
        },
        onComplete: function() {
            console.log("Class enumeration complete.");
        }
    });
});
```

结果如下：

```
Attaching...                                                                                                                                                                16:15:52 [120/187]
Loaded class: org.apache.http.HttpEntityEnclosingRequest
Loaded class: org.apache.http.ProtocolVersion
Loaded class: org.apache.http.HttpResponse
Loaded class: org.apache.http.impl.cookie.DateParseException
Loaded class: org.apache.http.message.AbstractHttpMessage
Loaded class: org.apache.http.HeaderIterator
Loaded class: org.apache.http.HttpHost
Loaded class: org.apache.http.params.AbstractHttpParams
Loaded class: org.apache.http.message.BasicHeader
Loaded class: org.apache.http.StatusLine
Loaded class: org.apache.http.client.methods.HttpUriRequest
Loaded class: org.apache.http.conn.ClientConnectionManager
Loaded class: org.apache.http.HttpEntity
Loaded class: org.apache.http.Header
Loaded class: org.apache.http.client.HttpClient
Loaded class: org.apache.http.NameValuePair
Loaded class: org.apache.http.message.BasicStatusLine
Loaded class: org.apache.http.message.BasicHttpResponse
Loaded class: org.apache.http.impl.cookie.DateUtils
Loaded class: org.apache.http.client.ResponseHandler
Loaded class: org.apache.http.client.methods.HttpEntityEnclosingRequestBase
Loaded class: org.apache.http.client.methods.AbortableHttpRequest
Loaded class: org.apache.http.client.methods.HttpRequestBase
Loaded class: org.apache.http.HttpVersion
Loaded class: org.apache.http.HttpRequest
Loaded class: org.apache.http.HttpMessage
Loaded class: org.apache.http.client.utils.URLEncodedUtils
Loaded class: org.apache.http.client.methods.HttpPost
Loaded class: org.apache.http.entity.BasicHttpEntity
Loaded class: org.apache.http.message.HeaderGroup
Loaded class: org.apache.http.params.BasicHttpParams
Loaded class: org.apache.http.protocol.HttpContext
Loaded class: org.apache.http.entity.AbstractHttpEntity
Loaded class: org.apache.http.params.HttpConnectionParams
Loaded class: org.apache.http.params.CoreConnectionPNames
Loaded class: org.apache.http.params.HttpParams
Loaded class: org.apache.http.conn.ConnectTimeoutException
Loaded class: com.android.okhttp.internal.http.HttpTransport
Loaded class: com.android.okhttp.Headers
Loaded class: com.android.okhttp.internal.tls.OkHostnameVerifier
Loaded class: com.android.okhttp.internal.http.RequestException
Loaded class: com.android.okhttp.internal.huc.HttpsURLConnectionImpl
Loaded class: com.android.okhttp.Connection
Loaded class: com.android.okhttp.ConnectionSpec
Loaded class: com.android.okhttp.internal.http.CacheStrategy
Loaded class: com.android.okhttp.internal.http.HttpMethod
Loaded class: com.android.okhttp.internal.huc.HttpURLConnectionImpl
Loaded class: com.android.okhttp.internal.OptionalMethod
Loaded class: com.android.okhttp.ConnectionPool$1
Loaded class: com.android.okhttp.internal.Util
Loaded class: com.android.okhttp.OkHttpClient$1
Loaded class: com.android.okhttp.internal.Network$1
Loaded class: com.android.okhttp.internal.http.HttpConnection$ChunkedSource
Loaded class: com.android.okhttp.RequestBody
Loaded class: com.android.okhttp.Headers$Builder
Loaded class: com.android.okhttp.CacheControl$Builder
Loaded class: com.android.okhttp.HttpUrl
Loaded class: com.android.okhttp.HttpHandler$CleartextURLFilter
Loaded class: com.android.okhttp.internal.http.OkHeaders$1
Loaded class: com.android.okhttp.okio.AsyncTimeout$1
Loaded class: com.android.okhttp.CertificatePinner$Builder
Loaded class: com.android.okhttp.Route
Loaded class: com.android.okhttp.Handshake
Loaded class: com.android.okhttp.okio.AsyncTimeout$2
Loaded class: com.android.okhttp.okio.BufferedSink
Loaded class: com.android.okhttp.internal.http.RouteException
Loaded class: com.android.okhttp.internal.http.Transport
Loaded class: com.android.okhttp.okio.RealBufferedSink$1
Loaded class: com.android.okhttp.Dispatcher
Loaded class: com.android.okhttp.okio.RealBufferedSink
Loaded class: com.android.okhttp.internal.http.OkHeaders
Loaded class: com.android.okhttp.internal.http.HttpEngine
Loaded class: com.android.okhttp.internal.http.HttpConnection$FixedLengthSource
Loaded class: com.android.okhttp.internal.Util$1
Loaded class: com.android.okhttp.Request
Loaded class: com.android.okhttp.okio.Source
Loaded class: com.android.okhttp.okio.RealBufferedSource$1
Loaded class: com.android.okhttp.TlsVersion
Loaded class: com.android.okhttp.HttpUrl$Builder$ParseResult
Loaded class: com.android.okhttp.OkUrlFactory
Loaded class: com.android.okhttp.okio.Timeout$1
Loaded class: com.android.okhttp.okio.ForwardingTimeout
Loaded class: com.android.okhttp.internal.Network
Loaded class: com.android.okhttp.internal.http.StatusLine
Loaded class: com.android.okhttp.internal.Internal
Loaded class: com.android.okhttp.internal.ConnectionSpecSelector
Loaded class: com.android.okhttp.CipherSuite
Loaded class: com.android.okhttp.HttpHandler
Loaded class: com.android.okhttp.ConnectionSpec$Builder
Loaded class: com.android.okhttp.Address
Loaded class: com.android.okhttp.ConfigAwareConnectionPool$1
Loaded class: com.android.okhttp.internal.http.HttpConnection$AbstractSource
Loaded class: com.android.okhttp.ConfigAwareConnectionPool
Loaded class: com.android.okhttp.okio.Timeout
Loaded class: com.android.okhttp.ConnectionPool
Loaded class: com.android.okhttp.okio.RealBufferedSource
Loaded class: com.android.okhttp.okio.SegmentPool
Loaded class: com.android.okhttp.okio.BufferedSource
Loaded class: com.android.okhttp.okio.Okio
Loaded class: com.android.okhttp.okio.Okio$1
Loaded class: com.android.okhttp.Response$Builder
Loaded class: com.android.okhttp.internal.http.RequestLine
Loaded class: com.android.okhttp.internal.http.RouteSelector
Loaded class: com.android.okhttp.okio.Okio$2
Loaded class: com.android.okhttp.ResponseBody
Loaded class: com.android.okhttp.okio.Okio$3
Loaded class: com.android.okhttp.Authenticator
Loaded class: com.android.okhttp.Response
Loaded class: com.android.okhttp.internal.http.RetryableSink
Loaded class: com.android.okhttp.HttpsHandler
Loaded class: com.android.okhttp.Protocol
Loaded class: com.android.okhttp.okio.Segment
Loaded class: com.android.okhttp.internal.huc.DelegatingHttpsURLConnection
Loaded class: com.android.okhttp.okio.Util
Loaded class: com.android.okhttp.okio.AsyncTimeout
Loaded class: com.android.okhttp.RequestBody$2
Loaded class: com.android.okhttp.okio.Sink
Loaded class: com.android.okhttp.internal.http.CacheStrategy$Factory
Loaded class: com.android.okhttp.CertificatePinner
Loaded class: com.android.okhttp.internal.RouteDatabase
Loaded class: com.android.okhttp.internal.http.HttpEngine$1
Loaded class: com.android.okhttp.HttpUrl$Builder
Loaded class: com.android.okhttp.internal.http.RealResponseBody
Loaded class: com.android.okhttp.internal.URLFilter
Loaded class: com.android.okhttp.internal.http.HttpConnection
Loaded class: com.android.okhttp.okio.AsyncTimeout$Watchdog
Loaded class: com.android.okhttp.internal.Platform
Loaded class: com.android.okhttp.CacheControl
Loaded class: com.android.okhttp.Request$Builder
Loaded class: com.android.okhttp.OkHttpClient
Loaded class: com.android.okhttp.internal.http.AuthenticatorAdapter
Loaded class: com.android.okhttp.okio.Buffer
Loaded class: [Lcom.android.okhttp.HttpUrl$Builder$ParseResult;
Loaded class: [Lorg.apache.http.Header;
Loaded class: [Lcom.android.okhttp.Protocol;
Loaded class: [Lcom.android.okhttp.ConnectionSpec;
Loaded class: [Lcom.android.okhttp.TlsVersion;
Loaded class: [Lcom.android.okhttp.CipherSuite;
Class enumeration complete.
```

可见其用了 `org.apache.http` 和 `com.android.okhttp` 这两个库，于是我们可以编写 hook 代码，这里以 `OkHttp` 的 `Request` 和 `Response` 为例：

```javascript
Java.perform(function() {
    var OkHttpRequestBuilder = Java.use('com.android.okhttp.Request$Builder');

    OkHttpRequestBuilder.build.implementation = function() {
        var request = this.build();
        var url = request.url().toString();
        console.log("[OkHttp] Request URL: " + url);

        // Print headers
        var headers = request.headers();
        for (var i = 0; i < headers.size(); i++) {
            console.log("[OkHttp] Header: " + headers.name(i) + ": " + headers.value(i));
        }

        return request;
    };

    var OkHttpClient = Java.use('com.android.okhttp.OkHttpClient');
    OkHttpClient.newCall.overload('com.android.okhttp.Request').implementation = function(request) {
        console.log("[OkHttp] Making request to: " + request.url().toString());
        return this.newCall(request);
    };
});
```

然后运行：

```sh
frida -U -n com.bidau.nkngl -l monitor_network.js
```

然后发现报错了，`frida-server`并没有在运行。于是我只好乖乖地去GitHub上下载了一份对应版本的`frida-server`，然后 push 到手机上，再启动服务端。

```sh
HWSTF:/data/local/tmp # ./frida-server-16.4.8-android-arm64 
unable to stat file for the executable "/memfd:frida-helper-32 (deleted)": No such file or directory
^CHWSTF:/data/local/tmp # 
```

这次再运行脚本，登了一段时间，并没有任何输出：

```sh
> frida -U -n com.bidau.nkngl -l monitor_network.js

     ____
    / _  |   Frida 16.4.8 - A world-class dynamic instrumentation toolkit
   | (_| |
    > _  |   Commands:
   /_/ |_|       help      -> Displays the help system
   . . . .       object?   -> Display information about 'object'
   . . . .       exit/quit -> Exit
   . . . .
   . . . .   More info at https://frida.re/docs/home/
   . . . .
   . . . .   Connected to STF AL10 (id=xxx)
                                                                                
[STF AL10::com.bidau.nkngl ]->
```

于是我选择了速度更快的静态分析，使用 jadx-gui 打开 apk 文件，根据今年六月份的实训经验，java 代码的业务逻辑基本都在`service`这个类中，于是我打开`com.nantu.nengl.service.MyLocalService`，找到了如下一段代码：

```java
    public boolean a(List<com.nantu.nengl.a.b> list) {
        if (list == null || list.size() == 0) {
            return true;
        }
        JSONObject jSONObject = new JSONObject();
        try {
            jSONObject.put("action", "openAppLogFromShuaji");
            JSONObject jSONObject2 = new JSONObject();
            jSONObject2.put("imei", com.nantu.nengl.c.d.a(this));
            jSONObject2.put("appverCode", f.a().a(this));
            jSONObject2.put("channelid", f.f45a);
            jSONObject2.put("imsi", com.nantu.nengl.c.d.b(this));
            jSONObject2.put("androidver", Build.VERSION.SDK_INT);
            JSONArray jSONArray = new JSONArray();
            for (int i = 0; i < list.size(); i++) {
                com.nantu.nengl.a.b bVar = list.get(i);
                if (bVar != null) {
                    JSONObject jSONObject3 = new JSONObject();
                    jSONObject3.put("p", bVar.b());
                    jSONObject3.put("m", bVar.c());
                    jSONObject3.put("nf", bVar.d());
                    jSONObject3.put("o", bVar.a());
                    jSONArray.put(jSONObject3);
                }
            }
            jSONObject2.put("applist", jSONArray);
            b.b("sendActiveApp l = " + jSONArray.toString());
            jSONObject.put("data", com.nantu.nengl.c.a.a(jSONObject2.toString(), "SJ@WWW.7TU.CN_AM"));
            return com.nantu.nengl.c.c.a(jSONObject.toString());
        } catch (JSONException e) {
            e.printStackTrace();
            return false;
        } catch (Exception e2) {
            e2.printStackTrace();
            return false;
        }
    }
```

原来这是我之前给手机安装的一个名为“奇兔刷机”的应用，这个应用现在都还躺在我的recovery分区里，感觉应该是没什么问题的。

#### com.android.vending

但是我总得通过什么东西来证明 frida 的能力对吧，于是我选择了 play 商店，包名是 `com.android.vending`，hook脚本不变。

但这次运行却出错了：

```sh
> frida -U -n com.android.vending -l monitor_network.js

     ____
    / _  |   Frida 16.4.8 - A world-class dynamic instrumentation toolkit
   | (_| |
    > _  |   Commands:
   /_/ |_|       help      -> Displays the help system
   . . . .       object?   -> Display information about 'object'
   . . . .       exit/quit -> Exit
   . . . .
   . . . .   More info at https://frida.re/docs/home/
   . . . .
   . . . .   Connected to STF AL10 (id=xxx)
Failed to spawn: unable to find process with name 'com.android.vending'
```

这个问题其实也不难解决，只需要拿到 play 商店的 pid，然后用 pid 进行 hook 也未尝不可，然后在 play 商店随便刷新几下就有结果了：

```sh
> frida -U -p 19507 -l monitor_network.js

     ____
    / _  |   Frida 16.4.8 - A world-class dynamic instrumentation toolkit
   | (_| |
    > _  |   Commands:
   /_/ |_|       help      -> Displays the help system
   . . . .       object?   -> Display information about 'object'
   . . . .       exit/quit -> Exit
   . . . .
   . . . .   More info at https://frida.re/docs/home/
   . . . .
   . . . .   Connected to STF AL10 (id=xxx)

[STF AL10::PID::19507 ]-> [OkHttp] Header: Host: play.googleapis.com                                          
[OkHttp] Header: Connection: Keep-Alive                                                        
[OkHttp] Header: Accept-Encoding: gzip                                                               
[OkHttp] Header: Content-Length: 7913                                       
[OkHttp] Request URL: https://play.googleapis.com/play/log?format=raw&proto_v2=true             
[OkHttp] Header: Content-Encoding: gzip                                                             
[OkHttp] Header: Content-Type: application/x-gzip                                                    
[OkHttp] Header: User-Agent: Android-Finsky/42.2.27-23%20%5B0%5D%20%5BPR%5D%20660620715                                 
[OkHttp] Header: Authorization: Bearer ya29.m.CpYCAdJUhWdHMq07ko1_QNsNqX0-6Z-sSqLuep-11xDbDzGwmbv40T_07xA6gzicGOdtIRL6BdTI5JroLxax1-PsRCElhVFFthKPXEmG2AR12LAVPlHI8JmLjVh5mxng7oEE2qQroDGusu5RruzqkIFOQu06qFBCr......................................................................................................................................................0SWQyTtdD0blEqv--9e6-yV3gR6vGOXROTIRWhCCdS2LF7phuO84eAXRjx6kkM-YSDwgBEgcKAQQQjeoEGMHNBBogVmnWzORig8HgDXTx0_LY_IwnqMpxpyfFd9kGW0AYE_IiAggBKithQ2dZS0FTQVNBUk1TRlFIR1gyTWlaT25kXzQ0anJwSjZHaklHMUxtSFBB
...
```

完结撒花。
