# nonebot_plugin_broker
本插件旨在提供简单易用的发布/订阅接口，以便迅速地向nonebot插件中加入推送功能，实现订阅的集中管理，避免重复代码<br>
此外也是一个简单的、插件之间信息交互的发布/订阅模式实现
## 安装
暂未发布，如需使用可以clone本库
## 简单使用
本插件提供三个对外函数，<code>register</code>/<code>subscribe</code>/<code>remove</code><br>
通过nonebot的<code>require</code>功能获得：<br>
>register = require("broker").register<br>
>subscribe = require("broker").subscribe<br>
>remove = require("broker").remove

使用register函数即可注册一个服务，并获得一个发布函数
