layout: post

title: 如何打造一个究极舒适的pwn环境（第三季）

author: junyu33

tags: 

- pwn
- linux

categories: 

- develop

date: 2022-5-23 22:00:00

---

在物理机上安装ubuntu20.04并配置常用软件和kernel pwn环境。

<!-- more -->

# ubuntu20.04安装

## 创建启动盘

在网上下载ubuntu20.04的iso文件后，使用UltraISO将U盘刻录为RAW格式。

**注意是RAW格式，不是什么USB-HDD+之类的东西，不然安装程序都进不去！**

重启进BIOS时，把U盘的优先级提到`hard drive`前面。

## 安装ubuntu

此时系统会让你试用或者安装，我的做法是先试用，再点安装程序。

试用的界面相当于一个可以上网的PE，你可以体验完后~~直接关机~~继续安装。

建议在体验过程中使用`Gparted`给硬盘分区，在硬盘的末端分出100G，左边60G给根目录，右边40G给用户目录，格式ext4。swap分区可以不用，缺点就是开机速度稍微慢一点。这样安装的时候就不用再折腾分区了。

安装过程中建议选择完整安装**但不下载更新**（否则安装将巨慢无比）。正常情况半小时足以安装好。

## 换源

`sudo vim /etc/apt/sources.list`

```bash
#添加阿里源
deb http://mirrors.aliyun.com/ubuntu/ focal main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ focal main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ focal-security main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ focal-security main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ focal-updates main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ focal-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ focal-proposed main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ focal-proposed main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ focal-backports main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ focal-backports main restricted universe multiverse
#添加清华源
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-updates main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-updates main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-backports main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-backports main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-security main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-security main restricted universe multiverse multiverse
```

`sudo apt-get update`

## 输入法

ubuntu自带的用起来感觉还行，基于iBus，不需要怎么配置。

https://blog.csdn.net/weixin_43431593/article/details/106444769

## 搭梯子

> 众所周知，如果你有了梯子，找梯子就很容易；但是如果你没有，找梯子就很麻烦。

如果使用了VPN，也许可以从官网上下载到天朝特供版的下载链接，省去了不少麻烦。

如果使用了机场，虽然拷贝订阅链接很简单，但是从github上下载客户端却很麻烦。建议在先前的系统中下载好linux版本，然后在ubuntu直接安装。

# 终端环境配置

> 原文地址：https://blog.csdn.net/weixin_41179606/article/details/80957817
>
> 在安装zsh-syntax-highlighting时原文有错误，笔者已修正。

```bash
# 默认当前路径为用户主目录
# 安装zsh
sudo apt-get install zsh
# 提示错误：Unable to locate package，则需要手动更新软件源
sudo apt-get update
# 安装完成之后，从shell切换为zsh
chsh -s /bin/zsh

sudo apt-get install git

sh -c "$(curl -fsSL https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"

# 安装autojump
sudo apt-get install autojump
# 打开配置文件
vim .zshrc
# 末尾添加下述语句
. /usr/share/autojump/autojump.sh

# 安装zsh-autosuggestions
git clone git://github.com/zsh-users/zsh-autosuggestions $ZSH_CUSTOM/plugins/zsh-autosuggestions
# 打开配置文件
vim .zshrc
# 添加配置1
plugins	= (
	git
	zsh-autosuggestions  // 此句为增写设置
)
# 添加配置2（文件末尾末尾）
source $ZSH_CUSTOM/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh

# 安装zsh-syntax-highlighting
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git
echo "source ${(q-)PWD}/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" >> ${ZDOTDIR:-$HOME}/.zshrc
source ./zsh-syntax-highlighting/zsh-syntax-highlighting.zsh

# 打开配置文件
vim .zshrc
# 修改ZSH_THEME
ZSH_THEME="ys"或"agnoster"

source ~/.zshrc
```

# 软件安装

现在你有了魔法而且换了源，安装软件或者拉取项目的时候，就不用考虑网络的问题了。

## 软件列表

- chrome
- netease music
- virtual box
- vscode
- intellij IDEA
- typora
- albert
- fsearch
- python3 (pip3)
  - pwntools
  - ropgadget, ropper
  - gdb, peda, gef, pwndbg, pwngdb
- ruby (gem)
  - one_gadget
- qemu
- docker
- IDA pro
- tencent meeting
- wechat
- ~~tim~~

## 从apt源安装

```bash
# install
sudo apt install *
# OR sudo apt-get install *
# remove
sudo apt remove *
# OR sudo apt-get remove *
```

## 安装deb文件

大多数应用都是这样安装的

```bash
# install
sudo dpkg -i *.deb
# remove
sudo dpkg -r *.deb
```

## 使用非国产系windows应用

大部分可以用wine搞定。

```bash
sudo dpkg --add-architecture i386 
wget -nc https://dl.winehq.org/wine-builds/winehq.key
sudo mv winehq.key /usr/share/keyrings/winehq-archive.key
wget -nc https://dl.winehq.org/wine-builds/ubuntu/dists/focal/winehq-focal.sources
sudo mv winehq-focal.sources /etc/apt/sources.list.d/
sudo apt update
sudo apt install --install-recommends winehq-stable
```

还是要一两个G的，安装有点费时。

只不过ida的一些配置比较麻烦，这里得写一下：

### IDA 配置

这里默认读者用的是免安装版的ida。

#### 坑一

直接用wine打开ida似乎会导致dll无法加载，从而ida的各种功能无法使用。

写了两个脚本指定了python的路径：

```bat
# start.bat
@set path=.\python-3;%path%
@set PYTHONPATH=.\python-3
@start ida.exe
# start64.bat
@set path=.\python-3;%path%
@set PYTHONPATH=.\python-3
@start ida64.exe
```

然后：

```bash
wine start.bat
wine start64.bat
```

> 有时会出现idapython无法加载的玄学错误，我的解决方案是在桌面建立ida根目录的软链接，从桌面打开shell进入软链接，再用wine运行这两个bat。
>
> 但是直接cd绝对路径就会报错，不知道什么原因。

#### 坑二

这个时候，ida本体和idapython已经可以正常使用了，但是部分插件，例如`findcrypt`、`keypatch`依然存在缺少`yara`、`keystone-engine`插件的问题。

安装方法见坑三。

~~由于我们的python是免安装版的，自然使用pip安装插件不会奏效。~~

~~我的做法是先安装一个**32位**python，**不添加到环境变量**，然后找到pip路径，运行`pip install xxx`，查看多了哪些文件，再手动的按照相对路径copy到免安装版python的路径中。~~

> ~~一个方便查看多了哪些文件的方法是，尝试卸载这个插件，然后shell将会显示将要删除哪些文件，这些文件就是安装后多出来的文件。~~

#### 坑三

> 原文链接：https://github.com/polymorf/findcrypt-yara/issues/34

即使你走到了这一步，依然还会存在一点问题，就是在使用`findcrypt`插件时会报错。

github的做法是卸载`yara`，安装`yara-python`，~~然而我试了，由于wine的特殊性，好像没用。~~

先用python执行`get-pip.py`，然后找到`python38._pth`文件，新建一行`Lib\site-packages`，然后就可以愉快地用pip安装包了。

一个简单粗暴的解决方法在`findcrypt3.rules`是删掉这个规则：

![](https://user-images.githubusercontent.com/37646748/103058572-73556f80-45dd-11eb-9ebf-b4a4c1a2e25a.png)


## 尝试使用国产系windows应用

### 网易云音乐

> deepin yyds!

https://www.deepin.org/zh/cooperative/netease-cloud-music/

### 腾讯会议

有原生linux版，可能是因为钉钉有linux版所以腾讯才舍得研发个原生版。

### 微信

#### 优麒麟原生版（未测试）

https://www.ubuntukylin.com/applications/106-cn.html

#### 使用deepinwine

https://blog.csdn.net/qq_40756508/article/details/107511334

### ~~tim/qq~~

#### 官方远古原生版

https://im.qq.com/linuxqq/index.html

二维码扫不了，艹了。

#### deepinwine

很容易崩溃，基本上就是一登录就崩溃。

暂时没有好的解决方案。

#### docker

https://github.com/top-bettercode/docker-qq

启动脚本把`fcitx`都改成`ibus`可以输入中文。

2022年6月13日实测可用。

缺点：接收的文件不能直接打开，必须使用docker shell从虚拟环境中拷贝出来。

```bash
# 10f0ec600caf是容器的id，可以通过sudo docker ps命令获得
sudo docker cp 10f0ec600caf:'/TencentFiles/2658799217/FileRecv/RV.rar' ~/Desktop
```

# kernel pwn环境搭建

> 部分内容来源于 https://kiprey.gitee.io/2021/10/kernel_pwn_introduction/

## 内核下载与编译

这里有一个项目打包了所有下载、解压、编译、打包rootfs的过程，还是很方便的。

https://github.com/pwncollege/pwnkernel

```bash
git clone https://github.com/pwncollege/pwnkernel.git
./build.sh
./launch.sh
# 由于在launch.sh中提供了打包rootfs的操作，因此只需要将编译好的驱动放到_install文件夹即可。
```

## gdb attach与调试

```bash
# 一定要提前指定架构
set architecture i386:x86-64
gef-remote --qemu-mode localhost:1234

# qemu 指定 -S 参数后挂起，此时在gdb键入以下命令
add-symbol-file vmlinux
b start_kernel
continue

[Breakpoint 1, start_kernel () at init/main.c:837]
......
```

## 启动脚本（未测试）

```bash
#! /bin/bash

# 判断当前权限是否为 root，需要高权限以执行 gef-remote --qemu-mode
user=$(env | grep "^USER" | cut -d "=" -f 2)
if [ "$user" != "root"  ]
  then
    echo "请使用 root 权限执行"
    exit
fi

# 复制驱动至 rootfs
cp ./mydrivers/*.ko busybox-1.32.0/_install

# 构建 rootfs
pushd busybox-1.32.0/_install
find . | cpio -o --format=newc > ../../rootfs.img
popd

# 启动 qemu
qemu-system-x86_64 \
    -kernel ./arch/x86/boot/bzImage \
    -initrd ./rootfs.img \
    -append "nokaslr" \
    -s  \
    -S&

    # -s ： 等价于 -gdb tcp::1234， 指定 qemu 的调试链接
    # -S ：指定 qemu 启动后立即挂起

    # -nographic                # 关闭 QEMU 图形界面
    # -append "console=ttyS0"   # 和 -nographic 一起使用，启动的界面就变成了当前终端

gnome-terminal -e 'gdb -x mygdbinit'
```

mygdbinit:

```bash
set architecture i386:x86-64
add-symbol-file vmlinux
gef-remote --qemu-mode localhost:1234

b start_kernel
c
```

## 上传脚本

> 从校赛扒过来的，配合本目录的exp.c使用。

```python
#!/usr/bin/python
from pwn import *

HOST = "127.0.0.1"
PORT =  25000

USER = "pwn"
PW = "pwn"

def compile():
    # sudo apt install musl-tools
    log.info("Compile")
    os.system("musl-gcc -w -s -masm=intel  -static -o3 exp.c -o pwn")

def exec_cmd(cmd):
    r.sendline(cmd)
    r.recvuntil("$ ")

def upload():
    p = log.progress("Upload")

    with open("pwn", "rb") as f:
        data = f.read()

    encoded = base64.b64encode(data)
    
    r.recvuntil("$ ")
    
    for i in range(0, len(encoded), 300):
        p.status("%d / %d" % (i, len(encoded)))
        exec_cmd("echo \"%s\" >> benc" % (encoded[i:i+300]))
        
    exec_cmd("cat benc | base64 -d > bout")    
    exec_cmd("chmod +x bout")
    
    p.success()

def exploit(r):
    compile()
    upload()
    context.log_level = "debug"
    r.interactive()

    return

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # session = ssh(USER, HOST, PORT, PW)
        # r = session.run("/bin/sh")
        HOST = "43.155.90.127"
        PORT = 25000 
        r = remote(HOST, PORT)
        exploit(r)
    else:
        r = process("./boot.sh")
        print(util.proc.pidof(r))
        pause()
        exploit(r)
```

