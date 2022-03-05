import time
import asyncio
from typing import Callable, Coroutine, List, Dict, Union, Any

import nonebot
from nonebot import require
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import MessageSegment, Message
# from nonebot.internal.adapter.message import Message

scheduler = require("nonebot_plugin_apscheduler").scheduler

SIMPLE_INFO_TYPE = Union[None, str, int, bytes, MessageSegment, Message]
COMPLEX_INFO_TYPE = List[SIMPLE_INFO_TYPE]
INFO_TYPE = Union[SIMPLE_INFO_TYPE, COMPLEX_INFO_TYPE]


def _parse_simple_info(info: SIMPLE_INFO_TYPE):
    '''
    分析info并构造MessageSegment
    '''
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
    '''
    分析info构造Message
    '''
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


def beijing2UTC(hour: Union[str, int]):
    '''
    FIXME:临时用着，等上游apscheduler修好了就删
    '''
    if isinstance(hour, int):
        hour -= 8
        if hour < 0:
            hour += 24
    return hour


class topic:
    '''
    订阅的基本单元，所有操作最终都由topic对象执行

    成员变量:
        name:                topic名称，用于完整描述topic工作内容
        title:               topic标题，同时也是topic主键
        aliases:             topic别名，通过别名也可以访问到topic
        cron:                cron定时器的各项参数，以dict表示，以存储至文件中，运行时无作用
        immediately:         是否立即发送，如为True，后续信息都会立即发送
        no_check:            如为True则不进行生命计数
        info:                将要推送的数据
        cache:               上次推送的数据
        to_callable:         当不为None时，将会对函数订阅者发送此变量
        last_send:           上次推送时间戳
        last_publish:        上次发布时间戳
        check_count:         生命计数器，达到一定数值后释放对象，暂未实装
        job:                 scheduler.job对象，内部使用
        subscriber:          来自外部的订阅者，在备份时间或bot关闭时会写入存储文件
        subscriber_callable: 来自bot内部的函数订阅者，不会存储到文件里

    方法：
        pack:    在存储时调用，将成员变量打包成dict，方便存储
        update:  重复register同一个title时，会使用本方法更新topic
        publish: 在调用register时，会返回topic对象的这个方法，用以发布内容
        subscribe: 订阅时，最终执行的方法
        remove:    退订时，最终执行的方法
        send:    推送内容的方法，未来可能将实现拆成独立模块
    '''
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
        '''
        将topic对象打包成dict，方便保存数据
        '''
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
        '''
        topic构造方法

        参数:
            title:       同成员变量
            hour:        传入scheduler使用
            name:        同成员变量
            aliases:     同成员变量
            immediately: 同成员变量
            no_check:    同成员变量
            subscriber:  直接传入订阅者列表，一般用来读取文件中的数据，不在代码中使用
            kwarg:       传入scheduler使用，具体参数参考apscheduler
        '''
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
        '''
        重复调用register时使用本方法更新topic，参数同__init__方法
        '''
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
        '''
        发布用的方法

        参数:
            info:        需要推送的消息，接受多种形式的参数
            to_callable: 该参数不为None时，会将该参数推送给函数订阅者
            immediately: 本次发布是否需要立即推送，只影响本次发布，不影响topic
        '''
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
        '''
        订阅操作的最终执行方法

        参数:
            subscriber: 订阅者
            type_:      订阅者类型，现在一般为"users"或"groups"
        '''
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
        '''
        退订操作的最终执行方法

        参数:
            subscriber: 订阅者
            type_:      订阅者类型，现在一般为"users"或"groups"
        '''
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
        '''
        推送内容方法
        '''
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
                if asyncio.iscoroutinefunction(func):
                    await func(self.info)
                func(self.info)
            else:
                if asyncio.iscoroutinefunction(func):
                    await func(self.to_callable)
                func(self.to_callable)
                self.to_callable = None
