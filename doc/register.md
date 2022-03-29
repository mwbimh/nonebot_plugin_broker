# register函数

register函数可以接收以下参数：

|参数名|类型|默认值|功能|
|:-:|:-:|:-:|:-:|
|title|str|""|服务的唯一标识符。订阅时首先会检查title是否符合
|hour|str \| int|8|字面意思，发送时间，支持cron表达式
|name|str|""|服务全名，如果使用，建议整个辨识度高一点的名字。在订阅时，如果没有匹配的title，则会检查name
|aliases|list[str]|[]|服务别名。在订阅时，如果title和name均不匹配，则会检查aliases
|immediately|bool|False|是否立刻推送。设定该服务是否在发布者发布后立刻向订阅者进行推送
|hide|bool|False|是否隐藏该服务。隐藏后所有用户均无法看到或订阅该服务，但对callable订阅者无效
|no_check|bool|False|是否进行存活检测。存活检测暂未实装，故无卵用
|subscriber|dict|{}|普通订阅者名单。用于将持久化数据读回服务，不建议使用
|black_list|dict|{}|黑名单。字面意思，也用于将持久化数据读回服务，不建议使用

除了以上参数，其他参数均会被传递给apscheduler.trigger.cron，您可以参考[这个页面](https://apscheduler.readthedocs.io/en/latest/modules/triggers/cron.html#module-apscheduler.triggers.cron)来自由定制您的服务在什么时候开始推送

***由于上游的一些小问题，可能不会自动修正时差，使用时请自行注意***
