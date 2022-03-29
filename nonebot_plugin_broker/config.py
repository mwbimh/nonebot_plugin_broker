from typing import Union, List, Dict
from pydantic import BaseSettings
from ruamel.yaml import YAML
from pathlib import Path

from nonebot import get_driver

from .topic import topic

BASE_PATH = Path("Data/broker")
TOPICS_PATH = BASE_PATH / "topics.yml"
yaml = YAML()


class Config(BaseSettings):
    broker_default_time: Union[int, str] = 8
    broker_store_time: Union[int, str] = 0
    broker_admin: Dict[str, List[Union[str, int]]] = {}
    broker_command_add: list = ["订阅"]
    broker_command_rm: list = ["退订"]
    broker_command_ls: list = ["清单"]
    broker_command_ban: list = ["ban"]
    broker_command_unban: list = ["unban"]
    broker_command_p_ls: list = ["完整清单"]

    def __init__(self, *arg, **kwarg) -> None:
        super().__init__(*arg, **kwarg)
        if self.broker_command_add == []:
            self.broker_command_add = ["订阅"]
        if self.broker_command_rm == []:
            self.broker_command_rm = ["退订"]
        if self.broker_command_ls == []:
            self.broker_command_ls = ["清单"]
        if self.broker_command_ban == []:
            self.broker_command_ban = ["ban"]
        if self.broker_command_unban == []:
            self.broker_command_unban = ["unban"]
        if self.broker_command_p_ls == []:
            self.broker_command_p_ls = ["完整清单"]

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
