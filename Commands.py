import os
import Func.MusicDownloader
import discord
import DefCommands
import Func.RecT
import Func.EpicGames
import asyncio
import subprocess
from Func.MusicDownloader import spoter, MusicT
from typing import Optional
from Comp.Ids import BLog
from discord.ext import commands
from discord import app_commands
from Comp.Ids import CMusic, CBot, CShoes, CInsta, CDiscord, Token

my_secret = Token
Id = CDiscord

#Define base
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)
Guild = discord.Object(id=Id)


async def Inc_channel(ctx):
  await ctx.response.send_message('Inccorect channel for that')
  await asyncio.sleep(3)
  await ctx.delete_original_response()


#Bot events
@bot.event
async def on_ready():
  await tree.sync(guild=discord.Object(id=Id))
  channel = bot.get_channel(BLog)
  await channel.send("connected")
  print("Ready!")
  await Func.RecT.charge_event(bot)
  #await StockShoes.StocksShoes(bot)
  #Install dependences
  command = 'pip install --upgrade yt-dlp'
  process = await asyncio.create_subprocess_shell(command,
                                                  stdout=subprocess.PIPE,
                                                  stderr=subprocess.PIPE)
  await process.communicate()
  if process.returncode == 0:
    print("Dependencia instalada exitosamente:")
  else:
    print("Error al instalar dependencia:")


@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  if message.channel == bot.get_channel(CMusic):
    bot_message = await message.channel.send(
      "Don't send that here. \n Only music commands, thanks.")
    await message.delete()
    await asyncio.sleep(3)
    await bot_message.delete()


@bot.event
async def on_interaction(interaction):
  await DefCommands.Log(interaction, bot)


#Autocomplet commands
@tree.command(name="hello", description="Greet me", guild=Guild)
async def helloT(interaction):
  if interaction.channel != bot.get_channel(CMusic):
    await DefCommands.hello(interaction)
  else:
    await Inc_channel(interaction)


@tree.command(name="bye", description="Good bye", guild=Guild)
async def byeT(interaction):
  if interaction.channel != bot.get_channel(CMusic):
    await DefCommands.bye(interaction)
  else:
    await Inc_channel(interaction)



@tree.command(name="change_discord", description="Set id", guild=Guild)
async def change_discord(ctx, id: int):
  Admin = await DefCommands.DetectAdmin(ctx)
  if Admin == True:
    if ctx.channel != bot.get_channel(CMusic):
      await DefCommands.change_discord(ctx, id)
    else:
      await Inc_channel(ctx)



#Download Music
@tree.command(name="d_music",
              description="Download music in mp3 format",
              guild=Guild)
async def DMusic(ctx, url: str):
  if ctx.channel == bot.get_channel(CMusic):
    await MusicT.music(ctx, url, bot)
  else:
    await Inc_channel(ctx)


@tree.command(name="get_playlist",
              description="Download a spotify playlist",
              guild=Guild)
async def DSpotify(ctx, url: str):
  if ctx.channel == bot.get_channel(CMusic):
    await spoter.set_up(ctx, url, bot)
  else:
    await Inc_channel(ctx)



@tree.command(name="ef",
              description="Generate sound effect",
              guild=Guild)
async def Def(ctx):
  await MusicT.ef(ctx, bot)



@tree.command(name="voice_disconnect",
              description="Disconnect the bot from the voice channel",
              guild=Guild)
async def Def_voice_disconnect(ctx):
  await MusicT.voice_disconnect(ctx, bot)



#Post insta
@tree.command(name="post_insta",
              description="Post a image to instagram",
              guild=Guild)
async def Post_instaT(ctx, prompt: str, custom_hashtaghs: str, url_imgs: str):
  Admin = await DefCommands.DetectAdmin(ctx)
  if Admin == True:
    if ctx.channel == bot.get_channel(CInsta):
      await Func.AI.Post_insta(ctx, bot, prompt, custom_hashtaghs, url_imgs)
    else:
      await Inc_channel(ctx)


#Music
@tree.command(name="play", description="Play a song", guild=Guild)
async def platT(ctx, url: str):
  if ctx.channel == bot.get_channel(CMusic):
    await Func.MusicDownloader.MusicT.play(ctx, url, bot)
  else:
    await Inc_channel(ctx)


class FileConverter(commands.Converter):

  async def convert(self, ctx, argument):
    if ctx.message.attachments:
      return ctx.message.attachments[0]
    raise commands.BadArgument(
      'No se ha proporcionado ningún archivo adjunto.')


#Change files format
@tree.command(name='format_file',
              description='Change the file format(Only compatible',
              guild=Guild)
async def format_fileT(ctx, file: str, format: str):
  if ctx.channel == bot.get_channel(CBot):
    await DefCommands.format_file(ctx, file, format)
  else:
    await Inc_channel(ctx)


#change a hexedecimal value to rgba
@tree.command(name="hex_rgba",
              description="Transform a Hexadecimal to rgba with max value 1",
              guild=Guild)
async def hex_rgbaT(ctx, value: str):
  if ctx.channel == bot.get_channel(CBot):
    await DefCommands.hex_rgba(ctx, value)
  else:
    await Inc_channel(ctx)


#Change pc mac
@tree.command(name="change_mac",
              description="Change you mac to another",
              guild=Guild)
async def change_macT(ctx, ip: str):
  if ctx.channel == bot.get_channel(CBot):
    await DefCommands.change_mac(ctx, ip)
  else:
    await Inc_channel(ctx)


#Short a url
@tree.command(name="tiny_url", description="Make a url shorter", guild=Guild)
async def tiny_urlT(ctx, url: str):
  if ctx.channel == bot.get_channel(CBot):
    await DefCommands.tiny_url(ctx, url)
  else:
    await Inc_channel(ctx)


#Epicgames notify
@tree.command(name="epicgames", description="Make a url shorter", guild=Guild)
async def EpicGamesT(ctx):
  await Func.EpicGames.main()
  


#Translate
@tree.command(name="trad", description="Translate a text", guild=Guild)
async def tradT(ctx, lang: str, text: str):
  if ctx.channel == bot.get_channel(CBot):
    await DefCommands.trad(ctx, lang, text)
  else:
    await Inc_channel(ctx)


#create remember events
@tree.command(name="reminder",
              description="Create a remember event",
              guild=Guild)
async def remT(ctx,
               message: str,
               minutes: int,
               hour: Optional[int] = None,
               day: Optional[int] = None,
               month: Optional[int] = None,
               user: Optional[str] = None):
  if ctx.channel == bot.get_channel(CBot):
    await Func.RecT.rem(ctx, message, hour, minutes, day, month, bot, user)
  else:
    await Inc_channel(ctx)



@tree.command(name='highlight',
              description='Only Admin(Highlight a message)',
              guild=Guild)
async def HighlightT(ctx,
                     title: str,
                     message: str,
                     description: Optional[str] = None,
                     url_image: Optional[str] = ''):
  Admin = await DefCommands.DetectAdmin(ctx)
  if Admin == True:
    await DefCommands.Highlight(ctx, title, message, description, url_image)



@tree.command(name="stop_bot", description="Only Admin", guild=Guild)
async def StopBot(ctx):
  Temp = await DefCommands.DetectAdmin(ctx)
  if Temp == True:
    await ctx.response.send_message("Stoping bot")
    await bot.close()
  else:
    await ctx.response.send_message("You are not admin")



@tree.command(
  name="deletall",
  description=
  "Delet all messages in that channel",
  guild=Guild)
async def deletallT(ctx):
  await DefCommands.deletall(ctx)



@tree.command(
  name="delet_messages",
  description=
  "Delet an specific number of messages",
  guild=Guild)
async def delet_messages(ctx, number: int):
  await DefCommands.delet_messages(ctx, number)



if __name__ == '__main__':
  bot.run(my_secret)