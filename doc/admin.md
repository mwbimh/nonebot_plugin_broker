# 管理员指令

现在支持三种管理员指令：`ban`、`unban`和`完整清单`，只有被指定为管理员的用户才能使用。

其中`ban`指令可以将某个用户加入某个服务的黑名单：

`/ban users 123456789 <服务标题1> <服务标题2> ...`

其中`users`为用户类型（现在可以为`users`或`groups`），`123456789`为用户id

如果不追加服务标题，如下：

`/ban users 123456789`

则会将该用户加入所有现存服务的黑名单

上述语句中`ban`均可替换为`unban`以将某用户移出黑名单

`/完整清单`可以列出接受broker管理的所有推送服务，无论是否隐藏或对该管理员是否可见