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
        self.duration = data.get('duration')

    async def get_data(self):
        print(self.data)

    @classmethod
    async def from_url(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, ytdl.extract_info, url)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, options=ffmpeg_options), data=data)


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

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
                del state
            except:
                pass

    @commands.command()
    async def summon(self, ctx):
        """Summons the bot to join your voice channel."""
        summoned_channel = ctx.author.voice.channel
        if summoned_channel is None:
            await self.bot.say('You are not in a voice channel.')
            return False

        state = self.get_voice_state(ctx.message.guild)
        if state.voice is None:
            # state.voice = await self.bot.join_voice_channel(summoned_channel)
            state.voice = await summoned_channel.connect()
        else:
            await state.voice.move_to(summoned_channel)

        return True

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel = None):
        """Joins a voice channel"""

        if channel is None:
            await ctx.send('You did not specify a channel!')

        state = self.get_voice_state(ctx.guild)

        if state.voice is not None:
            return await state.voice.move_to(channel)

        state.voice = await channel.connect()

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
            await ctx.send('No song specified!')
            return

        state = self.get_voice_state(ctx.guild)

        success = await ctx.invoke(self.summon)
        if not success:
            return

        try:
            source = await YTDLSource.from_url(url, loop=self.bot.loop)
        except Exception as e:
            fmt = 'An error occured while processing this request: ```py\n{}: {}\n```'
            await ctx.send(fmt.format(type(e).__name__, e))
        else:
            source.volume = 0.6
            entry = VoiceEntry(ctx.message, source)
            if state.songs.empty() and state.current is not None:
                await ctx.send(str(entry) + ' added to the queue.')
            await state.songs.put(entry)

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        state = self.get_voice_state(ctx.guild)

        if state.voice is None:
            return await ctx.send("Not connected to a voice channel.")

        state.current.volume = volume
        await ctx.send("Changed volume to {}%".format(volume))

    @commands.command()
    async def pause(self, ctx):
        """Pauses the currently playing audio."""
        state = self.get_voice_state(ctx.guild)

        if state.is_playing:
            state.voice.pause()
            await ctx.send('**Audio has been paused.**')
        else:
            await ctx.send('**No music is playing!**')

    @commands.command()
    async def resume(self, ctx):
        """Resumes the currently playing audio."""
        state = self.get_voice_state(ctx.guild)

        if not state.is_playing:
            state.voice.resume()
            await ctx.send('**Audio has been resumed.**')
        else:
            await ctx.send('**Audio is already playing!**')

    @commands.command()
    async def songdata(self, ctx):
        """Get song data. TEST"""
        state = self.get_voice_state(ctx.guild)

        if state.current is not None:
            await state.current.source.get_data()

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        state = self.get_voice_state(ctx.guild)

        try:
            state.audio_player.cancel()
            del self.voice_states[ctx.guild.id]
            await state.voice.disconnect()
        except:
            pass


class VoiceEntry:
    def __init__(self, message, source: YTDLSource):
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
        await self.current.channel.send('Skipped ' + str(self.current))
        if self.is_playing:
            self.voice.stop()

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            await self.current.channel.send('Now Playing ' + str(self.current))
            self.voice.play(self.current.source, after=lambda e: print('Player error: %s' % e) if e else None)


def setup(bot):
    bot.add_cog(Music(bot))
