layout: post

title: timeshift 使用 btrfs 懒人指南

author: junyu33

tags: 

- linux

categories: 

- develop

date: 2024-9-21 16:30:00

---

最近到了新工位，有了一台新电脑以及两台显示器。我深知系统备份的重要性，但因为沉没成本，一直没有来得及完全实装 btrfs 的备份恢复功能。因为新系统啥都没有，所以我可以肆无忌惮地折腾。这里记录一下我是如何使用 timeshift 的。

本文不涉及原理，以实用为主。

<!-- more -->

# 创建 btrfs 分区

对于一个新硬盘（笔者为 `/dev/nvme0n1`）：

- 你需要先创建一个 EFI 分区（512M），挂载到 `/boot/efi`
- 如果 RAM 小于 16G，建议创建一个 swap 分区（8G）。（但笔者的新电脑有 32G 内存，所以没有创建 swap 分区）
- 剩下的空间全部分给 btrfs

对应的命令为：

```bash
sudo fdisk /dev/nvme0n1

# 创建 GPT 分区表
g

# 创建 EFI 分区
n
# 分区号
<enter>
# 开始位置
<enter>
# 结束位置
+512M
# 分区类型
t
1
# remove signature
y

# 创建 btrfs 分区
n
# 分区号
<enter>
# 开始位置
<enter>
# 结束位置
<enter>
# remove signature
y

# 写入
w
```

# 格式化

现在有两个分区，一个 EFI 分区 `/dev/nvme0n1p1`，一个 btrfs 分区 `/dev/nvme0n1p2`。我们需要格式化这两个分区：

```bash
sudo mkfs.fat -F32 /dev/nvme0n1p1
sudo mkfs.btrfs -L arch /dev/nvme0n1p2
```

# btrfs 创建子卷（重要）

为了使 timeshift 可以正常工作，我们要达成以下效果：

```bash
> sudo btrfs subvolume list /
[sudo] password for junyu33: 
ID 256 gen 3073 top level 5 path @
ID 257 gen 3073 top level 5 path @home
```

具体的命令为：  

```bash
sudo mount /dev/nvme0n1p2 /mnt
sudo btrfs subvolume create /mnt/@
sudo btrfs subvolume create /mnt/@home
sudo umount /mnt
sudo mount -o subvol=@ /dev/nvme0n1p2 /mnt
sudo mkdir /mnt/home
sudo mount -o subvol=@home /dev/nvme0n1p2 /mnt/home
sudo mkdir -p /mnt/boot/efi
sudo mount /dev/nvme0n1p1 /mnt/boot/efi
```

# 安装系统

我不确定 xubuntu 是否会格式化 btrfs 分区（刚刚测试过，应该是，无法取消），如果是的话，我前面的步骤就白做了。所以我选择了 archlinux。安装过程就不赘述了，可以参考 [archlinux 安装指南](https://wiki.archlinux.org/title/Installation_guide)。

当你做到这一步时：

> `genfstab -U /mnt >> /mnt/etc/fstab`

看一看 `fstab` 文件的内容，并结合 `blkid` 的输出，确保 EFI 分区和 btrfs 的子卷（subvol）都被正确挂载，我的类似于：

```txt
# Static information about the filesystems.
# See fstab(5) for details.

# <file system> <dir> <type> <options> <dump> <pass>
# /dev/nvme0n1p2 LABEL=arch
UUID=d6806b41-d69c-4f72-ba9f-a00a197729ab	/         	btrfs     	rw,relatime,ssd,discard=async,space_cache=v2,subvolid=256,subvol=/@	0 0

# /dev/nvme0n1p2 LABEL=arch
UUID=d6806b41-d69c-4f72-ba9f-a00a197729ab	/home     	btrfs     	rw,relatime,ssd,discard=async,space_cache=v2,subvolid=257,subvol=/@home	0 0

# /dev/nvme0n1p1
UUID=EB74-8512      	/boot/efi 	vfat      	rw,relatime,fmask=0022,dmask=0022,codepage=437,iocharset=ascii,shortname=mixed,utf8,errors=remount-ro	0 2
```


此时你的 `/mnt` 目录应该类似于正常 Linux 的根目录，而不是 `@` 和 `@home`。

然后添加引导：

```bash
arch-chroot /mnt
pacman -S grub efibootmgr
grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=GRUB
grub-mkconfig -o /boot/grub/grub.cfg
```

然后退出 chroot，重启进入新系统。

# 安装 timeshift 并配置

```bash
# 安装 cronie 并启用 cron 服务
sudo pacman -S cronie
sudo systemctl enable cronie
# 安装 timeshift 及 grub-btrfs 插件
sudo pacman -S timeshift grub-btrfs
yay -S timeshift-systemd-timer
# 使 grub-btrfs 与 timeshift 配合
sudo systemctl edit --full grub-btrfsd
# 将 `grub-btrfsd --syslog /.snapshots` 修改为 `grub-btrfsd --syslog -t`
```

启动 `timeshift` 配置一下，搞定。