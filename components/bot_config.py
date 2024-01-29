# Description: Contains config file for bot
from pydantic import BaseSettings


class BotConfig(BaseSettings):
    DISCORD_BOT_TOKEN: str
    COMMANDS_PREFIX: str
    MUSIC_FOLDER: str

    class Config:
        env_file = "config/config.ini"
        env_file_encoding = "utf-8"
