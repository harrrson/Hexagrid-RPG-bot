from discord import VoiceChannel, DiscordException
from discord.ext import commands
import wavelink
import config

import re

URL_REG = re.compile(r'https?://(?:www\.)?.+')


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, 'wavelink'):  # This ensures the client isn't overwritten during cog reloads.
            self.bot.wavelink: wavelink.Client = wavelink.Client(bot=self.bot)

        self.bot.loop.create_task(self.start_nodes())

    async def start_nodes(self):
        nodes = {'MAIN': {'host': config.LAVALINK_HOST,
                          'port': config.LAVALINK_PORT,
                          'rest_uri': f'http://{config.LAVALINK_HOST}:{config.LAVALINK_PORT}',
                          'password': config.LAVALINK_PASSWORD,
                          'identifier': 'MAIN',
                          'region': 'eu_central'
                          }
                 }
        for n in nodes.values():
            await self.bot.wavelink.initiate_node(**n)

    @commands.group(invoke_without_command=True)
    async def music(self, ctx, command, *, args=None):
        return await ctx.send(f'No command found in module "music": {command}')

    @music.command(name="join")
    async def join_(self, ctx, *, channel=None):
        if channel and channel.isdigit():
            channel_temp = self.bot.get_channel(int(channel))
            if channel_temp.guild.id == ctx.message.guild.id:
                channel = channel_temp
        elif not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                raise DiscordException('No channel to join. Please either specify a valid channel or join one.')

        player = self.bot.wavelink.get_player(ctx.guild.id)
        await ctx.send(f'Connecting to **`{channel.name}`**')
        await player.connect(channel.id)

    @music.command(name="leave")
    async def leave_(self, ctx, *, args=None):
        # TODO add leave function
        pass

    @music.command()
    async def play(self, ctx, *, query: str):
        tracks = await self.bot.wavelink.get_tracks(f'ytsearch:{query}')

        if not tracks:
            return await ctx.send('Could not find any songs with that query.')

        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_connected:
            await ctx.invoke(self.join_)

        await ctx.send(f'Added {str(tracks[0])} to the queue.')
        await player.play(tracks[0])
        print(player.position)

    @music.command()
    async def stop(self, ctx, *, args=None):
        # TODO add stop command
        player = self.bot.wavelink.get_player(ctx.guild.id)
        print(player.position)

    @music.command()
    async def pause(self, ctx, *, args=None):
        # TODO add pause command
        print("pause")

    @music.command()
    async def resume(self, ctx, *, args=None):
        # TODO add resume function
        print('resume')


# def setup(bot):
#     bot.add_cog(Music(bot))
