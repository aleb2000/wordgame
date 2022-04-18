import os
import discord
import keep_alive
from discord.ext import commands
from wordgame import WordGame
from leaderboard import Leaderboard
from replit import db

TOKEN = os.getenv('DISCORD_TOKEN')

keep_alive.keep_alive()

bot = commands.Bot(command_prefix='$')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send(f"**{str(error)}**")
    elif isinstance(error, commands.ChannelNotFound):
        await ctx.send("**No channel has been chosen**")
    else:
        with open('err.log', 'a') as f:
            f.write(f"{str(error)}\n")

class Manage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.channel = None
        if "channel_id" in db.keys():
            self.bot.channel = self.bot.get_channel(int(db["channel_id"]))
        self.bot.leaderboard = Leaderboard()
        self.bot.leaderboard.load()
        print(self.bot.leaderboard.points)
        self.bot.game = WordGame(self.bot.leaderboard)
        self.bot.game.load()

    @commands.command(name="set-channel", help="Set the current channel as the channel to play the word game")
    async def set_channel(self, ctx):
        self.bot.channel = ctx.message.channel
        db["channel_id"] = ctx.message.channel.id
        await ctx.send("**This channel has been set as the word game channel**")

    @commands.command(name="get-channel", help="Get the channel that is currently set to play the word game")
    async def get_channel(self, ctx):
        if ctx.message.channel == self.bot.channel:
            await ctx.send("**This is the word game channel**")
        elif self.bot.channel:
            await ctx.send(f"**The channel currently set for the word game is <#{self.bot.channel.id}>**")
        else:
            await ctx.send("**No channel has been set for the word game**")

    async def cog_check(self, ctx):
        if discord.utils.get(ctx.author.roles, name="Word Master") == None:
            raise commands.MissingRole("Word Master")
        return True


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def valid_channel(self):
        if self.bot.channel == None:
            raise commands.ChannelNotFound(None)
        return True

    async def is_word_input(self, ctx):
        return ctx.message.channel == self.bot.channel and self.bot.game.has_started() and ctx.message.author != self.bot.user and not ctx.command

    @commands.command(name="start", help="Start a game")
    @commands.check(valid_channel)
    async def start(self, ctx):
        if self.bot.game.has_started():
            await ctx.send("**A game is already in progress, stop it before starting a new game.**")
        else:
            letter = self.bot.game.start()
            self.bot.game.save()
            await ctx.send(f"**The game is starting. The starting letter is `{letter}`.**")

    @commands.command(name="end", help="End the current game")
    @commands.check(valid_channel)
    async def end(self, ctx):
        if not self.bot.game.has_started():
            await ctx.send("**The game has not started**")
        else:
            await ctx.send("**The game has ended**")
            self.bot.game.end()
            self.bot.leaderboard.save()

    @commands.command(name="leaderboard", help="Show the leaderboard")
    @commands.check(valid_channel)
    async def leaderboard(self, ctx):
        embed = discord.Embed(title="Leaderboard", type="rich", description="The current leaderboard", color=0x11AA11)
        counter = 1
        for (id, score) in self.bot.leaderboard.sort().items():
            name = f"{counter}. {(await self.bot.fetch_user(id)).name}"
            embed.add_field(name=name, value=score, inline=False)
            counter += 1
        
        await ctx.send(embed=embed)

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        ctx = await self.bot.get_context(message)
        word = message.content.strip()
        if not await self.is_word_input(ctx) or word[0] == '.':
            return

        if " " in word:
            await message.reply("**Only a single word is accepted.**")
            return

        if self.bot.game.is_last_player(message.author.id):
            await message.reply("**You cannot answer two times in a row!**")
            return
        if self.bot.game.is_word_used(word):
            await message.reply("**This word was already used.**")
            return

        if self.bot.game.next_word(message.author.id, word):
            await message.add_reaction("\U00002705")
            self.bot.game.save()
        else:
            await message.reply(f"**Invalid word.**")


    async def cog_check(self, ctx):
        return ctx.message.channel == self.bot.channel

bot.add_cog(Manage(bot))
bot.add_cog(Game(bot))
bot.run(TOKEN)