# 插件配置

插件支持以下配置项：

`broker_default_time`: 调用register时如果不指定hour，则会使用该配置项，如果没有填写，则默认为8

`broker_store_time`: 每日定时保存订阅信息的时间，不填写则为默认值0

`broker_admin`: 插件管理员，填写时应遵循如下字典格式：

```python
{
    type1:[123456789],
    type2:[987654321]
}
```

其中type现在可为"users"和"groups"，后跟对应类别的id

下面为均为自定义指令名，类型均为列表（list），如果填写，请不要填[]

`broker_command_add`: 自定义订阅指令名，默认值为["订阅"]

`broker_command_rm`: 自定义退订指令名，默认值为["退订"]

`broker_command_ls`: 自定义拉清单指令名，默认值为["清单"]

`broker_command_ban`: 自定义管理员ban指令名，默认值为["ban"]

`broker_command_unban`: 自定义管理员unban指令名，默认值为["unban"]

`broker_command_p_ls`: 自定义管理员完整清单指令名，，默认值为["完整清单"]
