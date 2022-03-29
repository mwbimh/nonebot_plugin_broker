from typing import Dict, Any, List, Union

from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import (
    MessageEvent,
    PrivateMessageEvent,
    GroupMessageEvent
)

from .interface import (
    subscribe,
    remove,
    ls,
    ban,
    full_ban,
    unban,
    full_unban
)
from .config import config

regular_add = on_command(
    config.broker_command_add[0],
    aliases=set(config.broker_command_add[1:]),
    block=True,
    rule=to_me(),
    priority=2
)
regular_rm = on_command(
    config.broker_command_rm[0],
    aliases=set(config.broker_command_rm[1:]),
    block=True,
    rule=to_me(),
    priority=2
)
regular_ls = on_command(
    config.broker_command_ls[0],
    aliases=set(config.broker_command_ls[1:]),
    block=True,
    rule=to_me(),
    priority=2
)
privileged_ban = on_command(
    config.broker_command_ban[0],
    aliases=set(config.broker_command_ban[1:]),
    block=True,
    rule=to_me(),
    priority=2
)
privileged_unban = on_command(
    config.broker_command_unban[0],
    aliases=set(config.broker_command_unban[1:]),
    block=True,
    rule=to_me(),
    priority=2
)
privileged_ls = on_command(
    config.broker_command_p_ls[0],
    aliases=set(config.broker_command_p_ls[1:]),
    block=True,
    rule=to_me(),
    priority=2
)


@regular_add.handle()
async def add(event: MessageEvent):
    '''
    来自外部的订阅操作接收函数
    '''
    if _check(event):
        para = _parse(event)
        completed: List[str] = []
        for t in para["arg"]:
            if subscribe(t, subscriber=para["subscriber"], type_=para["type"]):
                completed.append(t)
        if len(completed) == 0:
            msg = "订阅失败，请检查参数"
        else:
            msg = "订阅成功，以下为本次订阅的服务:"
            for t in completed:
                msg += f"\n{t}"
        await regular_add.finish(msg)
    else:
        await regular_add.finish("权限不足无法订阅")


@regular_rm.handle()
async def rm(event: MessageEvent):
    '''
    来自外部的退订操作接收函数
    '''
    if _check(event):
        para = _parse(event)
        completed: List[str] = []
        for t in para["arg"]:
            if remove(t, subscriber=para["subscriber"], type_=para["type"]):
                completed.append(t)
        if len(completed) == 0:
            msg = "退订失败，请检查参数"
        else:
            msg = "退订成功，以下为本次退订的服务:"
            for t in completed:
                msg += f"\n{t}"
        await regular_rm.finish(msg)
    else:
        await regular_rm.finish("权限不足无法退订")


@regular_ls.handle()
async def get_list(event: MessageEvent):
    '''
    来自外部的请求清单操作接收函数
    '''
    if _check(event):
        para = _parse(event)
        li = ls(subscriber=para["subscriber"], type_=para["type"])
        if li == []:
            await regular_ls.finish("没有可订阅服务")
        else:
            msg = "可订阅服务清单:"
            i = 0
            for t in li:
                i += 1
                msg += f"\n{i}.{t}\n  title: {t.title}"
            await regular_ls.finish(msg)
    else:
        await regular_ls.finish("权限不足无法查询")


@privileged_ban.handle()
async def p_ban(event: MessageEvent):
    '''
    来自外部的管理员ban操作接收函数
    '''
    para = _parse(event)
    if _check_privilege(subscriber=para["subscriber"], type_=para["type"]):
        if len(para["arg"]) < 2:
            await privileged_ban.finish("参数不足")
        else:
            type_ = para["arg"][0]
            subscriber = para["arg"][1]
            arg = para["arg"][2:]
            if arg == []:
                full_ban(subscriber=subscriber, type_=type_)
                await privileged_ban.finish("处理完成")
            else:
                msg = "成功禁止下列服务:"
                for t in arg:
                    if ban(t, subscriber=subscriber, type_=type_):
                        msg += "\nt"
                await privileged_ban.finish(msg)
    else:
        await privileged_ban.finish("权限不足，无法执行")


@privileged_unban.handle()
async def p_unban(event: MessageEvent):
    '''
    来自外部的管理员解ban操作接收函数
    '''
    para = _parse(event)
    if _check_privilege(subscriber=para["subscriber"], type_=para["type"]):
        if len(para["arg"]) < 2:
            await privileged_unban.finish("参数不足")
        else:
            type_ = para["arg"][0]
            subscriber = para["arg"][1]
            arg = para["arg"][2:]
            if arg == []:
                full_unban(subscriber=subscriber, type_=type_)
                await privileged_unban.finish("处理完成")
            else:
                msg = "成功解禁下列服务:"
                for t in arg:
                    if unban(t, subscriber=subscriber, type_=type_):
                        msg += "\nt"
                await privileged_unban.finish(msg)
    else:
        await privileged_unban.finish("权限不足，无法执行")


@privileged_ls.handle()
async def p_ls(event: MessageEvent):
    para = _parse(event)
    if _check_privilege(subscriber=para["subscriber"], type_=para["type"]):
        li = ls(force=True)
        if li == []:
            await regular_ls.finish("没有可订阅服务")
        else:
            msg = "可订阅服务清单:"
            i = 0
            for t in li:
                i += 1
                msg += f"\n{i}.{t}\n  title: {t.title}"
            await regular_ls.finish(msg)


def _check(event: MessageEvent) -> bool:
    '''
    '''
    if isinstance(event, PrivateMessageEvent):
        return True
    elif isinstance(event, GroupMessageEvent):
        if event.sender.role in ["owner", "admin"]:
            return True
    return False


def _parse(event: MessageEvent) -> Dict[str, Any]:
    '''
    '''
    arg = event.get_plaintext().split()
    if isinstance(event, PrivateMessageEvent):
        subscriber = event.get_user_id()
        type_ = "users"
    elif isinstance(event, GroupMessageEvent):
        subscriber = str(event.group_id)
        type_ = "groups"
    else:
        return {"arg": []}
    return {
        "arg": arg[1:],
        "subscriber": subscriber,
        "type": type_
    }


def _check_privilege(
    subscriber: Union[str, int] = None,
    type_: str = None
) -> bool:
    return (
        type_ in config.broker_admin and
        subscriber in config.broker_admin[type_]
    )
