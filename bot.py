import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from wordgame import WordGame

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='$')
bot.channel = None
bot.game = WordGame()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send(f"**{str(error)}**")
    elif isinstance(error, commands.ChannelNotFound):
        await ctx.send("**No channel has been chosen**")

class Manage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="set-channel", help="Set the current channel as the channel to play the word game")
    async def set_channel(self, ctx):
        self.bot.channel = ctx.message.channel
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
            await ctx.send(f"**The game is starting. The starting letter is `{letter}`.**")

    @commands.command(name="end", help="End the current game")
    @commands.check(valid_channel)
    async def end(self, ctx):
        if not self.bot.game.has_started():
            await ctx.send("**The game has not started**")
        else:
            await ctx.send("**The game has ended**")
            self.bot.game.end()
    

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        ctx = await self.bot.get_context(message)
        word = message.content.strip().lower()
        if not await self.is_word_input(ctx) or word[0] == '.':
            return

        if " " in word:
            await message.reply("**Only a single word is accepted.**")
            return

        if self.bot.game.is_last_player(message.author):
            await message.reply("**You cannot answer two times in a row!**")
            return
        if self.bot.game.is_word_used(word):
            await message.reply("**This word was already used.**")
            return

        if self.bot.game.next_word(message.author, word):
            await message.add_reaction("\U00002705")
        else:
            await message.reply(f"**Word '{word}' is invalid.**")


    async def cog_check(self, ctx):
        return ctx.message.channel == self.bot.channel

bot.add_cog(Manage(bot))
bot.add_cog(Game(bot))
bot.run(TOKEN)
