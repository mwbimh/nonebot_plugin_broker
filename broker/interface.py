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
    try:
        t: topic = find_topic(title, topics)
        if t is None:
            raise ValueError(f"未找到该主题:{title}")
        return t.remove(*arg, **kwarg)
    except Exception as e:
        logger.error(f"取消订阅异常,异常信息:{e.__str__()}")
        return False


def find_topic(title: Union[str, int], topics: List[topic]) -> topic:
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
