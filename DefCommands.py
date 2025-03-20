from collections import deque
from Comp.Ids import CLog
#import googletrans
import asyncio
import datetime
import pyshorteners
import os
import discord
from Comp.Ids import CDiscord

log_file = "Comp/comands.log"
max_lines = 1200

#Registrar
async def Log(interaction, bot):
  # Obtener información del comando
  command = interaction.data.get('name')
  user = interaction.user.name
  channel = interaction.channel.name
  guild = interaction.guild.name

  # Crear registro
  log = f"-{user}-, Command: '{command}' Channel: '{channel}' server: '{guild}'"

  # Guardar registro en un archivo
  with open(log_file, "a", encoding='utf-8') as f:
    f.write(log + "\n")

  # Enviar registro al canal de Discord
  channel = await bot.fetch_channel(CLog)
  await channel.send(log)

  # Mantener las últimas 200 líneas del archivo de registro
  lines = deque(maxlen=max_lines)
  with open(log_file, "r", encoding='utf-8') as f:
    for line in f:
      lines.append(line.rstrip())

  # Sobrescribir el archivo de registro con las últimas 200 líneas
  with open(log_file, "w", encoding='utf-8') as f:
    f.write("\n".join(lines) + "\n")


#Comandos Básicos
async def hello(interaction):
  await interaction.response.send_message(f"Hello {interaction.user.mention}!")


async def bye(interaction):
  await interaction.response.send_message(f"Bye {interaction.user.mention}!")



async def change_discord(ctx, id):
  await ctx.response.send_message(f"Changing discord!")
  CDiscord = id
  with open('/Comp/Ids.py', 'w') as file:
        file.write(CDiscord)




#Traducir
async def trad(ctx, lang, text):
  lang = lang.lower()
  if lang not in googletrans.LANGUAGES and lang not in googletrans.LANGCODES:
    print("Invalid language")
  texts = ' '.join(text)
  translator = googletrans.Translator()
  translation = translator.translate(texts, dest=lang).text
  await ctx.response.send_message(
    f'Your text: {text} \ntranslated {translation}')


async def hex_rgba(ctx, value):
  r_norm = int(value[1:3], 16) / 255
  g_norm = int(value[3:5], 16) / 255
  b_norm = int(value[5:7], 16) / 255
  await ctx.response.send_message(f"RGBA: ({r_norm}, {g_norm}, {b_norm}, 1.0)")


async def tiny_url(ctx, url):
  type_tiny = pyshorteners.Shortener()
  short_link = type_tiny.tinyurl.short(url)
  await ctx.response.send_message(f'Shortest link: {short_link}')


async def format_file(ctx, file, format):
  print(file)


#Administrate
async def Highlight(ctx, title, message, description, url_image):
  await ctx.response.send_message('Done')
  message_unlock = message.replace('\\n', '\n')
  if description:
    description_unlock = description.replace('\\n', '\n')
  else:
    description_unlock = '--------------'
  embed = discord.Embed(title=title, description=description_unlock, color=discord.Color.purple())
  
  embed.set_author(name=ctx.user.name)
  embed.set_thumbnail(url=ctx.user.avatar)
  embed.set_image(url=url_image)
  embed.add_field(name='Message', value=message_unlock)
  
  await ctx.channel.send(embed=embed)
  await ctx.delete_original_response()


async def deletall(ctx):
  Result = await DetectAdmin(ctx)
  if Result == True:
    channel = ctx.channel
    await ctx.response.send_message("Deleting...")
    pinned = await channel.pins()
    await ctx.edit_original_response(content="Done")
    messages = []
    
    async for message in channel.history(limit=101):
      if message not in pinned:
        now_with_timezone = datetime.datetime.now(message.created_at.tzinfo)
        max_time = datetime.timedelta(days=14, hours=0, minutes=0, seconds=0)
        # Calcular el tiempo que lleva el mensaje con el bot
        time = now_with_timezone - message.created_at
        if time >= max_time:
          await message.delete()
          await asyncio.sleep(0.02)
        else:
          messages.append(message)
    await ctx.edit_original_response(content="Total messages: " +
                                     str(len(messages)))
    await asyncio.sleep(1)
    while messages:
      await channel.delete_messages(messages[:100])
      messages = messages[100:]
  else:
    await ctx.response.send_message("You are not an admin")



async def delet_messages(ctx, number):
  Admin = await DetectAdmin(ctx)
  if Admin == True:
    channel = ctx.channel
    await ctx.response.send_message("Deleting...")
    pinned = await channel.pins()
    await ctx.edit_original_response(content="Done")
    messages = []
    now_with_timezone = datetime.datetime.now(message.created_at.tzinfo)
    max_time = datetime.timedelta(days=14, hours=0, minutes=0, seconds=0)
    async for message in channel.history(limit=number+1):
      if message not in pinned:
        # Calcular el tiempo que lleva el mensaje con el bot
        time = now_with_timezone - message.created_at
        if time >= max_time:
          await message.delete()
          await asyncio.sleep(0.02)
        else:
          messages.append(message)
    await ctx.edit_original_response(content="Total messages: " +
                                     str(len(messages)))
    await asyncio.sleep(1)
    while messages:
      await channel.delete_messages(messages[:100])
      messages = messages[100:]
  else:
    await ctx.response.send_message("You are not an admin")



#@commands.is_owner()
async def DetectAdmin(interaction):
  channel = interaction.channel
  user = interaction.user
  permissions = channel.permissions_for(user)
  if permissions.administrator:
    return True
  else:
    return False
