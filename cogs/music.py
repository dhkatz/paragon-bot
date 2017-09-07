import asyncio

import discord
import youtube_dl
from gtts import gTTS

from discord.ext import commands

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'before_options': '-nostdin',
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=1):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, ytdl.extract_info, url)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music:
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, guild: discord.Guild):
        state = self.voice_states.get(guild.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[guild.id] = state

        return state

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def tts(self, ctx, *, query):
        """Have the bot join your channel and say what you said."""
        # Thanks to https://stackoverflow.com/questions/9893175/google-text-to-speech-api/31791632#31791632
        tts = gTTS(text=query, lang='en')
        tts.save('temp.mp3')

        if ctx.voice_client is None:
            if ctx.author.voice.channel:
                await ctx.author.voice.channel.connect()
            else:
                return await ctx.send("Not connected to a voice channel.")

        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('temp.mp3'))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

    @commands.command()
    async def playloc(self, ctx, *, query):
        """Plays a file from the local filesystem"""

        if ctx.voice_client is None:
            if ctx.author.voice.channel:
                await ctx.author.voice.channel.connect()
            else:
                return await ctx.send("Not connected to a voice channel.")

        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(query))

    @commands.command()
    async def play(self, ctx, *, url: str = ''):
        """Streams from a url (almost anything youtube_dl supports)"""

        if len(url) == 0:
            await ctx.channel.send('No song specified!')
            return

        state = self.get_voice_state(ctx.guild)

        if state.voice is None:
            success = await ctx.invoke(self.join)

        if ctx.voice_client is None:
            if ctx.author.voice.channel:
                await ctx.author.voice.channel.connect()
            else:
                return await ctx.send("Not connected to a voice channel.")

        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()

        player = await YTDLSource.from_url(url, loop=self.bot.loop)
        ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume
        await ctx.send("Changed volume to {}%".format(volume))

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()


class VoiceEntry:
    def __init__(self, message, source):
        self.requester = message.author
        self.channel = message.channel
        self.source = source

    def __str__(self):
        fmt = '**{0.title}**'
        duration = self.source.duration
        if duration:
            fmt = fmt + ' [{0[0]}m {0[1]}s]'.format(divmod(duration, 60))
        return fmt.format(self.source, self.requester)


class VoiceState:
    def __init__(self, bot):
        self.bot = bot
        self.voice = None
        self.current = None
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skips = set()
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    @property
    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        return self.voice.is_playing

    async def skip(self):
        self.skips.clear()
        await self.bot.send(self.voice.channel, 'Skipped ' + str(self.current))
        if self.is_playing:
            self.voice.stop()

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            await self.bot.send(self.voice.channel, 'Now Playing ' + str(self.current))
            self.voice.play(self.current.source, after=lambda e: print('Player error: %s' % e) if e else None)


def setup(bot):
    bot.add_cog(Music(bot))
