from discord.ext import commands

import wavelink
import config
import asyncio

import re

URL_REG = re.compile(r'https?://(?:www\.)?.+')


class BaseCogException(commands.CommandError):
    pass


class NotConnectedException(BaseCogException):
    pass


class NoCommonChannelException(BaseCogException):
    pass


class NoChannelSpecifiedException(BaseCogException):
    pass


class EmptyQueueException(BaseCogException):
    pass


class Player(wavelink.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = asyncio.Queue()
        self.context: commands.Context = kwargs.get('context', None)

        self.stopped = False

    async def do_next(self):
        if self.is_playing:
            return

        try:
            track = self.queue.get_nowait()
        except asyncio.QueueEmpty:
            return await self.context.send('Queue is empty!')

        await self.play(track)
        return track


class Music(commands.Cog, wavelink.WavelinkMixin):

    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, 'wavelink'):  # This ensures the client isn't overwritten during cog reloads.
            self.bot.wavelink: wavelink.Client = wavelink.Client(bot=self.bot)

        self.bot.loop.create_task(self.start_nodes())

    def check_player(self, guild_id):
        """Check, if player for guild exists"""
        for player in self.bot.wavelink.players:
            if self.bot.wavelink.players[player].guild_id == guild_id:
                return True
        return False

    async def start_nodes(self):

        if self.bot.wavelink.nodes:
            previous = self.bot.wavelink.nodes.copy()

            for node in previous.values():
                await node.destroy()

        nodes = {'MAIN': {'host': config.LAVALINK_HOST,
                          'port': config.LAVALINK_PORT,
                          'rest_uri': f'http://{config.LAVALINK_HOST}:{config.LAVALINK_PORT}',
                          'password': config.LAVALINK_PASSWORD,
                          'identifier': 'MAIN',
                          'region': 'eu_central'
                          }
                 }
        await self.bot.wait_until_ready()
        for n in nodes.values():
            await self.bot.wavelink.initiate_node(**n)

    @wavelink.WavelinkMixin.listener()
    async def on_node_ready(self, node: wavelink.Node):
        print(f'Node {node.identifier} is ready!')

    @wavelink.WavelinkMixin.listener('on_track_stuck')
    @wavelink.WavelinkMixin.listener('on_track_end')
    @wavelink.WavelinkMixin.listener('on_track_exception')
    async def on_player_stop(self, node: wavelink.Node, payload):
        if not payload.player.stopped:
            await payload.player.do_next()

    async def cog_command_error(self, ctx, error):
        if isinstance(error, NotConnectedException):
            await ctx.send("I am not connected to any channel.")
        elif isinstance(error, NoCommonChannelException):
            await ctx.send("You need to be on my channel to use this command!")
        elif isinstance(error, NoChannelSpecifiedException):
            await ctx.send('No channel to join. Please either specify a valid channel or join one.')
        elif isinstance(error, EmptyQueueException):
            await ctx.send('No more songs in queue!')
        else:
            raise error

    async def cog_check(self, ctx):
        if not ctx.guild:
            await ctx.send("Music commands are not available in PMs!")
            return False

        return True

    @commands.group(invoke_without_command=True)
    async def music(self, ctx, command, *, args=None):
        return await ctx.send(f'No command found in module "music": {command}')

    @music.command()
    async def join(self, ctx, *, channel=None):
        if channel and channel.isdigit():
            channel_temp = self.bot.get_channel(int(channel))
            if channel_temp.guild.id == ctx.message.guild.id:
                channel = channel_temp
        elif not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                raise NoChannelSpecifiedException

        player: wavelink.Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)
        if player.is_connected:
            await ctx.send(f"I am connected to channel <#{player.channel_id}>")

        await ctx.send(f'Connecting to **`{channel.name}`**')
        await player.connect(channel.id)

    @music.command()
    async def leave(self, ctx, *, args=None):
        if not self.check_player(ctx.guild.id):
            raise NotConnectedException

        player: wavelink.Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)
        if ctx.author.voice.channel.id != player.channel_id:
            raise NoCommonChannelException

        if player.is_playing:
            await ctx.invoke(self.stop)

        await player.destroy()

    @music.command()
    async def play(self, ctx, *, query: str):
        query = query.strip('<>')
        if not URL_REG.match(query):
            query = f'ytsearch:{query}'

        tracks = await self.bot.wavelink.get_tracks(query)

        if not tracks:
            return await ctx.send('Could not find any songs with that query.')

        player: wavelink.Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)
        if not player.is_connected:
            await ctx.invoke(self.join)
        player.stopped = False
        if isinstance(tracks, wavelink.TrackPlaylist):
            for track in tracks.tracks:
                await player.queue.put(track)

            await ctx.send(f'```ini\nAdded the playlist {tracks.data["playlistInfo"]["name"]}'
                           f' with {len(tracks.tracks)} songs to the queue.\n```')

            if not player.is_playing:
                await player.do_next()
        else:
            await ctx.send(f'Added {str(tracks[0])} to the queue.')
            if not player.is_playing:
                await player.play(tracks[0])
            else:
                player.queue.put(track[0])

    @music.command()
    async def stop(self, ctx, *, args=None):
        # TODO:
        if not self.check_player(ctx.guild.id):
            raise NotConnectedException

        player: wavelink.Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if ctx.author.voice.channel.id != player.channel_id:
            raise NoCommonChannelException

        if not player.is_playing:
            return await ctx.send("No music is actually played.")

        player.stopped = True
        await player.stop()
        await ctx.send("Song is stopped.")

    @music.command()
    async def next(self, ctx, *, args=None):
        if not self.check_player(ctx.guild.id):
            raise NotConnectedException

        player: wavelink.Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if ctx.author.voice.channel.id != player.channel_id:
            raise NoCommonChannelException

        player.stopped = False
        await player.stop()

    @music.command()
    async def pause(self, ctx, *, args=None):
        if not self.check_player(ctx.guild.id):
            raise NotConnectedException

        player: wavelink.Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if ctx.author.voice.channel.id != player.channel_id:
            raise NoCommonChannelException

        if not player.is_playing:
            return await ctx.send("No music is actually played.")

        if player.is_paused:
            return await ctx.send(
                f"Music is actually paused. Type \"{ctx.prefix}music resume\" to resume played music.")

        await player.set_pause(True)

    @music.command()
    async def resume(self, ctx, *, args=None):
        if not self.check_player(ctx.guild.id):
            raise NotConnectedException

        player: wavelink.Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if ctx.author.voice.channel.id != player.channel_id:
            raise NoCommonChannelException

        if not player.is_playing:
            return await ctx.send("No music is actually played.")

        if not player.is_paused:
            return await ctx.send(f"Music is actually playing.")

        await player.set_pause(False)

    @music.command()
    async def queue(self, ctx, *, args=None):
        if not self.check_player(ctx.guild.id):
            raise NotConnectedException

        player: wavelink.Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if ctx.author.voice.channel.id != player.channel_id:
            raise NoCommonChannelException

        if player.queue.qsize() == 0:
            return await ctx.send('There are no more songs in the queue.')

        entries = [track.title for track in player.queue._queue]
        message = "```Actual queue:"
        for i, track in enumerate(entries, 1):
            track = f"\n{i}: {track}"
            if len(message + track) < 1900:
                message += track
            else:
                message += f"\n+ {player.queue.qsize() - i + 1} more songs"
                break
        message += "\n```"
        await ctx.send(message)

    @music.command()
    async def clear_queue(self, ctx, *, args=None):
        if not self.check_player(ctx.guild.id):
            raise NotConnectedException

        player: wavelink.Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if ctx.author.voice.channel.id != player.channel_id:
            raise NoCommonChannelException

        if player.queue.qsize() == 0:
            return await ctx.send('There are no more songs in the queue.')

        while player.queue.qsize() > 0:
            try:
                player.queue.get_nowait()
                player.queue.task_done()
            except asyncio.QueueEmpty:
                break

        await ctx.send("Query cleared!")

    @music.command(aliases=['playing', 'current', 'now_playing'])
    async def playing_(self, ctx, *, args):
        if not self.check_player(ctx.guild.id):
            raise NotConnectedException

        player: wavelink.Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if ctx.author.voice.channel.id != player.channel_id:
            raise NoCommonChannelException

        if not player.is_playing:
            return await ctx.send("No music is actually played.")

        if player.current is not None:
            await ctx.send(f"'''Current song: {player.current.title}'''")


def setup(bot):
    bot.add_cog(Music(bot))
