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
    hour: Union[str, int] = config.default_time,
    **kwarg
) -> Callable[[INFO_TYPE, Any, bool], bool]:
    '''
    注册topic，详见topic的构造方法
    '''
    t: topic = find_topic(title, topics)
    if t is None:
        t = topic(title=title, hour=hour, **kwarg)
        topics.append(t)
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
        logger.error(f"增加订阅异常,异常信息:{e.__str__()}")
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
        logger.error(f"取消订阅异常,异常信息:{e.__str__()}")
        return False


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
