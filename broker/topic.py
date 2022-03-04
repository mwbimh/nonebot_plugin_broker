import time
from datetime import datetime
from typing import Callable, Coroutine, List, Dict, Union, Any

import nonebot
from nonebot import require
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import MessageSegment, Message, Bot
# from nonebot.internal.adapter.message import Message

scheduler = require("nonebot_plugin_apscheduler").scheduler

SIMPLE_INFO_TYPE = Union[None, str, int, bytes, MessageSegment, Message]
COMPLEX_INFO_TYPE = List[SIMPLE_INFO_TYPE]
INFO_TYPE = Union[SIMPLE_INFO_TYPE, COMPLEX_INFO_TYPE]


def _parse_simple_info(info: SIMPLE_INFO_TYPE):
    if isinstance(info, str):
        return MessageSegment.text(info)
    elif isinstance(info, int):
        return MessageSegment.text(str(info))
    elif isinstance(info, bytes):
        return MessageSegment.image(info)
    elif isinstance(info, MessageSegment):
        return info
    return MessageSegment.text("")


def _construct_message(info: INFO_TYPE) -> Message:
    if isinstance(info, (str, int, bytes, MessageSegment, Message)):
        return _parse_simple_info(info)
    elif isinstance(info, list):
        msg: Message = None
        for it in info:
            if msg is None:
                msg = Message(_parse_simple_info(it))
            else:
                msg += _parse_simple_info(it)
        return msg
    return None


# FIXME:临时用着，等上游apscheduler修好了就删
def beijing2UTC(hour: Union[str, int]):
    if isinstance(hour, int):
        hour -= 8
        if hour < 0:
            hour += 24
    return hour


class topic:
    name: str = ""
    title: str = ""
    aliases: List[str] = None
    cron: Dict[Any, Any] = None
    immediately: bool = False

    no_check: bool = False  # 插件内部使用，不建议在外部调用时使用

    info: Message = None
    cache: Message = None
    to_callable: Any = None

    last_send: float = -1
    last_publish: float = -1
    check_count: int = 0

    job = None

    subscriber: Dict[str, List[Union[str, int]]] = None
    subscriber_callable: List[Callable[[Any], Any]] = None

    def pack(self):
        package = {
            "name": self.name,
            "title": self.title,
            "aliases": self.aliases,
            "immediately": self.immediately,
            "no_check": self.no_check,
            "subscriber": self.subscriber
        }
        package.update(self.cron)
        return package

    def __init__(
        self,
        title: str,
        hour: Union[str, int],
        name: str = "",
        aliases: List[str] = None,
        immediately: bool = False,
        no_check: bool = False,
        subscriber: Dict[str, List[Union[str, int]]] = None,
        **kwarg
    ) -> None:
        self.title = title
        self.name = name
        self.aliases = aliases if aliases is not None else []
        self.immediately = immediately
        self.no_check = no_check
        self.subscriber = subscriber if subscriber is not None else {}
        self.subscriber_callable = []
        if not immediately:
            self.job = scheduler.add_job(
                self.send,
                "cron",
                hour=beijing2UTC(hour),
                **kwarg
            )
            self.cron = kwarg
            self.cron["hour"] = hour
        logger.debug(f"{name} 注册完成")

    def update(
        self,
        hour: Union[str, int],
        name: str = "",
        aliases: List[str] = None,
        immediately: bool = False,
        no_check: bool = False,
        **kwarg
    ):
        if name != "":
            self.name = name
        if aliases is not None:
            self.aliases = aliases
        if self.immediately and not immediately:
            if self.job is None:
                self.job = scheduler.add_job(
                    self.send,
                    "cron",
                    hour=beijing2UTC(hour),
                    **kwarg
                )
                self.cron = kwarg
                self.cron["hour"] = hour
            else:
                self.job.reschedule("cron", **kwarg)
                self.job.resume()
                self.cron = kwarg
                self.cron["hour"] = hour
        elif not self.immediately and immediately:
            self.job.pause()
            self.cron = {}
        self.immediately = immediately
        self.no_check = no_check
        logger.debug(f"{self.name if self.name != '' else self.title} 更新完成")

    def publish(
        self,
        info: INFO_TYPE,
        to_callable: Any = None,
        immediately: bool = False
    ) -> bool:
        logger.debug(f"{self.name if self.name != '' else self.title} 准备发布")
        self.cache = self.info
        self.info = _construct_message(info)
        if to_callable is not None:
            self.to_callable = to_callable
        self.last_publish = time.time()
        if immediately:
            self.send()
            return True
        return True

    def subscribe(
        self,
        subscriber: Union[Union[str, int], Callable[[Any], Any]],
        type_: str = "callable"
    ) -> bool:
        logger.debug(f"{self.name if self.name != '' else self.title} 被订阅")
        if isinstance(subscriber, Callable):
            if subscriber in self.subscriber_callable:
                return False
            self.subscriber_callable.append(subscriber)
            return True
        if type_ not in self.subscriber:
            self.subscriber[type_] = []
        subscriber = str(subscriber)
        if subscriber in self.subscriber[type_]:
            return False
        self.subscriber[type_].append(str(subscriber))
        return True

    def remove(
        self,
        subscriber: Union[Union[str, int], Callable[[Any], Any]],
        type_: str
    ) -> bool:
        logger.debug(f"{self.name if self.name != '' else self.title} 被取消订阅")
        if isinstance(subscriber, Callable):
            if subscriber not in self.subscriber_callable:
                return False
            self.subscriber_callable.remove(subscriber)
            return True
        if type_ not in self.subscriber:
            return False
        subscriber = str(subscriber)
        if subscriber not in self.subscriber[type_]:
            return False
        self.subscriber[type_].remove(subscriber)
        return True

    async def send(self):
        if self.info is None:
            logger.warning(
                f"{self.name if self.name != '' else self.title} 未准备好"
            )
            return
        if self.last_send > self.last_publish:
            self.check_count += 1
        self.last_send = time.time()
        logger.info(
            f"{self.name if self.name != '' else self.title} 正在推送"
        )
        # print(nonebot.get_bots())
        # print(4)
        # print(nonebot.get_bot())
        # print(self.info)
        if "users" in self.subscriber:
            for user in self.subscriber["users"]:
                await nonebot.get_bot().send_private_msg(
                    user_id=int(user),
                    message=self.info
                )
        if "groups" in self.subscriber:
            for group in self.subscriber["groups"]:
                await nonebot.get_bot().send_group_msg(
                    group_id=int(group),
                    message=self.info
                )
        for func in self.subscriber_callable:
            if self.to_callable is None:
                if isinstance(func, Coroutine):
                    await func(self.info)
                func(self.info)
            else:
                if isinstance(func, Coroutine):
                    await func(self.to_callable)
                func(self.to_callable)
