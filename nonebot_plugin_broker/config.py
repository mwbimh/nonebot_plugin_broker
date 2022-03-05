from typing import Union, List
from pydantic import BaseSettings
from ruamel.yaml import YAML
from pathlib import Path

from nonebot import get_driver

from .topic import topic

BASE_PATH = Path("Data/broker")
TOPICS_PATH = BASE_PATH / "topics.yml"
yaml = YAML()


class Config(BaseSettings):
    default_time: Union[int, str] = 8
    store_time: Union[int, str] = 0

    class Config:
        extra = "ignore"


def load_topics() -> List[topic]:
    '''
    读取已保存的数据
    '''
    try:
        t = yaml.load(TOPICS_PATH)
        if t is None:
            return []
        return yaml.load(TOPICS_PATH)
    except Exception:
        pass
    return []


async def save_topics(topics: List[topic]):
    '''
    将数据存入yml文件
    '''
    if not TOPICS_PATH.exists():
        TOPICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    _temp = []
    for t in topics:
        _temp.append(t.pack())
    yaml.dump(_temp, TOPICS_PATH)

global_config = get_driver().config
config = Config.parse_obj(global_config)
