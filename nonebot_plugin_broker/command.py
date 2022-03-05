from typing import Dict, Any, List

from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import (
    MessageEvent,
    PrivateMessageEvent,
    GroupMessageEvent
)

from .interface import register, subscribe, remove

regular_add = on_command(
    "订阅",
    aliases=set(["订", "加", "加订", "add", "subscribe", "sub"]),
    block=True,
    rule=to_me(),
    priority=2
)
regular_rm = on_command(
    "退订",
    aliases=set(["退", "停", "remove", "unsubscribe", "rm"]),
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
