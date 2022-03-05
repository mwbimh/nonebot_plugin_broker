# nonebot_plugin_broker

本插件旨在提供简单易用的发布/订阅接口，以便迅速地向nonebot插件中加入推送功能，实现订阅的集中管理，避免重复代码

此外也是一个简单的、插件之间信息交互的发布/订阅模式实现

## 安装

可以使用`pip`安装

```shell
pip install nonebot_plugin_broker
```

如果使用脚手架`nb-cli`，也许可以:

```shell
nb plugin install nonebot_plugin_broker
```

## 简单使用

本插件提供三个对外函数，`register`/`subscribe`/`remove`
通过nonebot的`require`功能获得：

```python
register = require("broker").register
subscribe = require("broker").subscribe
remove = require("broker").remove
```

### 发布

使用register函数即可注册一个服务，并获得一个发布函数

```python
publish = register(title="test", hour=8)
```

其中`title`参数是该服务的标题，也是该服务的唯一标识符，使用时请避免重名

`hour`参数为该服务的推送时间，`hour=8`代表会在每天早上八点进行推送

`hour`参数可以省略，如果省略，则会使用`.env`文件中的

`default_time`变量，如果没有该变量，则默认为8，即早上八点。
这两个参数还可以在保持位置关系的条件下省略参数名，故上述语句可以简写为：

```python
publish = register("test")
```

也是同样的功能

在注册完服务，得到publish函数后，便可在插件中向broker发布内容了：

```python
def func(arg):
    do_something
    ...
    publish("a test info")
    ...
    do_something
```

如上，发布完成后，broker会在指定的时间向订阅者推送消息，发布者无需对订阅和推送进行管理

当然，publish不仅可以发布字符串消息，也支持发送数字（会被转换成字符串）和bytes类型的图片，或是包含上述内容的列表list，如果仍未满足需求，可以自行组装`MessageSegment`发送

### 订阅

对于想要订阅已注册服务的用户，可以向bot发送`/订阅 <服务标题1> <服务标题2> ...`进行订阅，指令和参数间、参数和参数间需要有空格分割，如果是一个群需要订阅，则需要群主/管理员 @bot 发送如上指令：`@bot /订阅 <服务标题1> <服务标题2> ...`

退订流程同上，将`订阅`换成`退订`即可

对于想要订阅已注册服务的开发者，可以使用`subscribe`函数：

```python
def func(arg):
    do_something

subscribe(title="test", subscriber=func)
```

如上，即可使`func`成为`test`服务的订阅者，broker会将消息作为参数传入该函数并调用之

退订方法也同上，只需将`subscribe`换成`remove`

***请注意：送入该函数通常是`Message`对象而非原始数据，您可能需要自行进行解析***

### 其他

插件同时还自带了每个小时的报时服务、每月第一天早上八点的报时服务 及每周一早上八点的报时服务，这些服务在被函数订阅时将不会送入`Message`对象：

| 服务 | 标题（title） | 参数   |
|   :-:   |   :-:   |   :-:   |
|x点报时服务 |clock{x}|   {x}   |
|月初报时服务|月初通知 |first_day|
|周一报时服务|周一通知 |   mon   |

## 进阶使用

先鸽着

## 示例

简单的使用方法可以参考我的[leetcode_everyday插件](https://github.com/mwbimh/nonebot_plugin_leetcode_everyday)

## TODO

以下为近期更新目标

- 完善基础功能
- 加入管理功能，支持管理员向bot发送信息进行管理
- 向bot请求服务清单的功能
- 支持mirai适配器
- 写文档？

## 未来做什么

以下内容在考虑中

- 支持更多适配器，在本插件上抹平适配器间的差异（主要是文字和图片）
- 其他不知道什么鬼功能

如果您有什么想法也可以告诉我

## LICENSE

MIT License
