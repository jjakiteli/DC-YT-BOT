import discord
from discord.ext import commands

from components.bot_config import BotConfig
from components.music.bot_music import MusicComponent


class DiscordBot:
    TOKEN: str
    client: commands.Bot

    def __init__(self) -> None:
        self.TOKEN = BotConfig().DISCORD_BOT_TOKEN
        PREFIX = BotConfig().COMMANDS_PREFIX
        intents = discord.Intents().default()
        intents.message_content = True
        self.client = commands.Bot(
            command_prefix=PREFIX, case_insensitive=True, intents=intents
        )

    def run_discord_bot(self):
        @self.client.event
        async def on_ready():
            try:
                print(f"{self.client.user} is ready to work!!!")
            except Exception as e:
                print(e)

        @self.client.event
        async def on_connect():
            print(f"{self.client.user} has connected to Discord!")

        @self.client.event
        async def on_disconnect():
            print(f"{self.client.user} has disconnected from Discord!")

        @self.client.event
        async def on_error(event, *args, **kwargs):
            print(
                f"!!!{self.client.user} has encountered an error!!!"
                + str(event)
                + str(args)
                + str(kwargs)
            )

        @self.client.event
        async def on_command_error(context, exception):
            print(
                f"!!!{self.client.user} has encountered a command error!!!"
                + str(exception)
            )

        MusicComponent(self.client)
        self.client.run(self.TOKEN)


if __name__ == "__main__":
    DiscordBot().run_discord_bot()
