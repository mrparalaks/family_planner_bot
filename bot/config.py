from dataclasses import dataclass
from environs import Env

@dataclass
class BotConfig:
    token: str
    admin_ids: list[int]

@dataclass
class Config:
    bot: BotConfig

def load_config() -> Config:
    env = Env()
    env.read_env()
    return Config(
        bot=BotConfig(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMIN_IDS"))),
        )
    )
