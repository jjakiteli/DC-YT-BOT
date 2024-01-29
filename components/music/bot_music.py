import platform
import threading
import time

import discord
from discord.ext import commands

from components.music.YTDL import YTDLSource
from components.bot_config import BotConfig


class MusicComponent:
    client: commands.Bot
    voice_client: discord.VoiceClient = None
    playlist: list[str] = []
    current_song_name: str = None

    def __init__(self, client):
        self.client = client
        threading.Thread(target=self.update_playlist).start()

        @self.client.event
        async def on_voice_state_update(member, before, after):
            if member != self.client.user:
                return
            if self.voice_client is not None:
                if after.channel is None:
                    self.voice_client = None

        @self.client.command(name="play", help="Play youtube video (url)")
        async def play(ctx, url):
            if self.voice_client is not None:
                if self.voice_client.channel != ctx.message.author.voice.channel:
                    await leave(ctx)

            if self.voice_client is None:
                if not ctx.message.author.voice:
                    await ctx.send(
                        f"{ctx.message.author.name} is not connected to a voice channel"
                    )
                    return
                else:
                    channel = ctx.message.author.voice.channel
                await channel.connect()
                self.voice_client = ctx.message.guild.voice_client

            async with ctx.typing():
                filename = await YTDLSource.from_url(url)
                self.playlist.append(filename)
            if platform.system() == "Windows":
                prefix = BotConfig().MUSIC_FOLDER.replace("./", "")
                trimmed_filename = (
                    filename.replace(f"{prefix}\\", "").replace(".webm", "").replace("'", "")
                )
            else:
                trimmed_filename = (
                    filename.replace(f"{BotConfig().MUSIC_FOLDER}/", "").replace(".webm", "").replace("'", "")
                )
            await ctx.send(f"**Added to playlist:** {trimmed_filename}")

        @self.client.command(name="lookup", help="Lookup the playlist")
        async def lookup(ctx):
            if len(self.playlist) != 0:
                if platform.system() == "Windows":
                    prefix = BotConfig().MUSIC_FOLDER.replace("./", "")
                    trimmed_list = [
                        s.replace(f"{prefix}\\", "").replace(".webm", "").replace("'", "")
                        for s in self.playlist
                    ]
                else:
                    trimmed_list = [
                        s.replace(f"{BotConfig().MUSIC_FOLDER}/", "").replace(".webm", "").replace("'", "")
                        for s in self.playlist
                    ]
                trimmed_list = "\n".join(trimmed_list)
                await ctx.send(f"**Playlist:** \n{trimmed_list}")

        @self.client.command(name="skip", help="Skips the current song")
        async def skip(ctx):
            if self.voice_client.is_playing():
                await ctx.send(f"Skipping song {self.current_song_name}")
                await self.voice_client.stop()

        @self.client.command(name="clear", help="Clears the playlist")
        async def clear(ctx):
            if self.voice_client.is_playing():
                self.playlist.clear()
                await ctx.send("Cleared playlist")

        @self.client.command(name="leave", help="Make bot leave the voice channel")
        async def leave(ctx):
            if self.voice_client.is_connected():
                await self.voice_client.disconnect()
                await clear(ctx)
                self.voice_client = None

    def update_playlist(self):
        while not self.client.is_closed():
            if self.voice_client is not None:
                if not self.voice_client.is_playing():
                    if len(self.playlist) > 0:
                        filename = self.playlist.pop(0)
                        if platform.system() == "Windows":
                            self.voice_client.play(
                                discord.FFmpegPCMAudio(
                                    executable="ffmpeg.exe", source=filename
                                )
                            )
                        elif platform.system() == "Linux":
                            self.voice_client.play(
                                discord.FFmpegPCMAudio(
                                    executable="ffmpeg", source=filename
                                )
                            )
                        else:
                            raise Exception("Unsupported OS")
                        self.current_song_name = filename
                    else:
                        self.current_song_name = None
            time.sleep(1)
