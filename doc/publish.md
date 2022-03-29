# publish函数

publish可以接收以下参数：
|参数名|类型|默认值|功能|
|:-:|:-:|:-:|:-:|
|info|str \| int \| bytes \| MessageSegment|无|需要发布的消息
|to_callable|Any|无|推送时向callable对象发送的参数
|immediately|bool|False|本次发布是否需要立即推送

***info支持文本和图片，其他内容仍在研究中***
