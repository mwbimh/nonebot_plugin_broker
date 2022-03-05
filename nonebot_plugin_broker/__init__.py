from typing import List

from nonebot.plugin import export
from nonebot import get_driver, require
from nonebot.log import logger

from .topic import topic
from .config import Config, load_topics, save_topics
from .interface import register, subscribe
from . import command
from . import internal

for t in load_topics():
    register(**t)

for i in range(24):
    publish = register(
        name=f"每日{i}点报时服务",
        title=f"clock{i}",
        hour=i,
        no_check=True
    )
    publish(info=f"现在是北京时间{i}点整", to_callable=i)

# ***一些没啥用的服务
publish = register(
    name=f"每月第一天通知服务",
    title=f"月初通知",
    day=1,
    no_check=True
)
publish(info=f"新的一个月到了", to_callable="first_day")

publish = register(
    name=f"周一通知服务",
    title=f"周一通知",
    day_of_week=0,
    no_check=True
)
publish(info=f"新的一周", to_callable="mon")
# ***一些没啥用的服务
