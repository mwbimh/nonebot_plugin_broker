# subscribe&remove函数

subscribe与remove有着类似的结构，均接收以下参数：
|参数|类型|功能|
|:-:|:-:|:-:|
|subscriber|str \| int|即订阅者id|
|type_|str|订阅者类型，如果是订阅者是callable，则无需该参数|
