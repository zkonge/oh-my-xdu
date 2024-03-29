# oh-my-xdu

![oh-my-xdu](art/ohmyxdu.svg)

[![License: CC0 1.0 Universal](https://img.shields.io/badge/License-CC0%201.0%20Universal-blue.svg)](https://creativecommons.org/publicdomain/zero/1.0)
[![PyPI version](https://badge.fury.io/py/oh-my-xdu.svg)](https://badge.fury.io/py/oh-my-xdu)

✨安全，便利，高拓展性的下一代西电校园生活脚本平台

# 🛑停止维护
由于校园服务变动，本项目似乎已经无法正常使用，同时由于作者已经毕业，没有继续维护的能力了。

项目现已属于公有领域。

## 需求
1. Python 3.7+
2. pip (全局安装)
3. venv (独立安装)

## 安装

### 使用 pip 全局安装

```shell script
$ pip install oh-my-xdu
```

### 独立安装（暂时不可用）

1. 类 Unix 平台
    ```shell script
    $ curl https://github.com/zkonge/oh-my-xdu/get-omx.py | python3
    ```

2. Windows (Powershell)
    ```shell script
    PS > (Invoke-WebRequest https://github.com/zkonge/oh-my-xdu/get-omx.py -UseBasicParsing).Content | python
    ```

## 使用

oh-my-xdu 由两大部分组成，认证服务和插件。

omx 中的认证服务有继承的机制，如果某种认证服务在本地缺失账号密码，那程序便会从上层继承已存在的账号密码，这种机制在使用者所有账号密码都相同的情况下非常方便。

程序会在第一次启动时记录学工号与密码（即IDS，统一身份认证的账号密码），并加密存储至磁盘上。这是认证服务最顶层的账号密码。

可以使用
```shell script
$ omx show
```
查看当前支持的插件列表。

如果需要更改密码，或者某些认证使用的账号密码与顶层不同，可使用
```shell script
$ omx credentials password zfw
```
修改密码，其中 password 为修改项，zfw 为认证名，在这里 zfw 可用于查询流量。

omx 有着齐全的代码文档与注释，使用帮助可在任意命令下添加 `-h` 参数调出。

## 第三方调用
请参考 samples 目录下文件

## 插件贡献开发者指南
暂时摸了，参考一下 ohmyxdu/plugins 吧

## 感谢
[xidian-scripts](https://github.com/xdlinux/xidian-scripts) 与其中所有的贡献者们

## 许可证
项目本体以 [CC0 1.0 Universal](LICENSE) 许可证发布

其中艺术作品字体来自于 [Ubuntu](https://design.ubuntu.com/font/)
