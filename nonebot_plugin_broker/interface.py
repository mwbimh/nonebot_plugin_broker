from typing import Callable, Union, Any, List

from nonebot.log import logger
from nonebot.plugin import export

from .topic import topic, INFO_TYPE
from .config import config

ex = export()
topics: List[topic] = []


@ex
def register(
    title: str,
    hour: Union[str, int] = config.broker_default_time,
    **kwarg
) -> Callable[[INFO_TYPE, Any, bool], bool]:
    '''
    注册topic，详见topic的构造方法
    '''
    t: topic = find_topic(title, topics)
    if t is None:
        t = topic(title=title, hour=hour, **kwarg)
        topics.append(t)
    else:
        t.update(hour=hour, **kwarg)
    return t.publish


@ex
def subscribe(
    title: Union[str, int],
    *arg,
    **kwarg
) -> bool:
    '''
    订阅topic，详见topic的subscribe方法
    '''
    try:
        t: topic = find_topic(title, topics)
        if t is None:
            raise ValueError(f"未找到该主题:{title}")
        return t.subscribe(*arg, **kwarg)
    except Exception as e:
        logger.error(f"增加订阅异常,异常信息:{e}")
        return False


@ex
def remove(
    title: Union[str, int],
    *arg,
    **kwarg
) -> bool:
    '''
    退订topic，详见topic的remove方法
    '''
    try:
        t: topic = find_topic(title, topics)
        if t is None:
            raise ValueError(f"未找到该主题:{title}")
        return t.remove(*arg, **kwarg)
    except Exception as e:
        logger.error(f"取消订阅异常,异常信息:{e}")
        return False


@ex
def ls(
    force: bool = False,
    **kwarg
) -> List[topic]:
    '''
    列出topic清单，返回元素为topic的list，force参数为true可以强制获取所有topic，其余参数详见topic的is_exposed方法
    '''
    if force:
        return topics.copy()
    li = []
    for t in topics:
        if t.is_exposed(**kwarg):
            li.append(t)
    return li


@ex
def ban(
    title: Union[str, int],
    *arg,
    **kwarg
) -> bool:
    '''
    将用户加入topic黑名单，详见topic的ban方法
    '''
    try:
        t: topic = find_topic(title, topics)
        if t is None:
            raise ValueError(f"未找到该主题:{title}")
        return t.ban(*arg, **kwarg)
    except Exception as e:
        logger.error(f"禁止订阅异常,异常信息:{e}")
        return False


@ex
def full_ban(*arg, **kwarg):
    '''
    将用户加入所有topic黑名单，详见topic的ban方法
    '''
    for t in topics:
        t.ban(*arg, **kwarg)


@ex
def unban(
    title: Union[str, int],
    *arg,
    **kwarg
) -> bool:
    '''
    将用户移出topic黑名单，详见topic的unban方法
    '''
    try:
        t: topic = find_topic(title, topics)
        if t is None:
            raise ValueError(f"未找到该主题:{title}")
        return t.unban(*arg, **kwarg)
    except Exception as e:
        logger.error(f"解禁订阅异常,异常信息:{e}")
        return False


@ex
def full_unban(*arg, **kwarg):
    '''
    将用户移出所有topic黑名单，详见topic的ban方法
    '''
    for t in topics:
        t.unban(*arg, **kwarg)


def find_topic(title: Union[str, int], topics: List[topic]) -> topic:
    '''
    从topics中找到title对应的topic，如果是整数则直接按编号获取，
    如果是字符串，则会先尝试匹配title，然后匹配name，最后再匹配aliases
    '''
    if isinstance(title, int):
        if title < len(topics):
            return topics[title]
    else:
        for t in topics:
            if t.title == title:
                return t
        for t in topics:
            if t.name == title:
                return t
        for t in topics:
            if title in t.aliases:
                return t
    return None
