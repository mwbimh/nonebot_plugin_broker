import nonebot
from nonebot.log import logger

from .config import save_topics, config
from .interface import subscribe, topics, register

driver = nonebot.get_driver()


@driver.on_startup
async def a():
    subscribe(config.store_time, subscriber=store)


@driver.on_shutdown
async def store(a=0):
    logger.debug("时机已至，存储订阅信息中")
    await save_topics(topics)
    logger.debug("存储完成")
