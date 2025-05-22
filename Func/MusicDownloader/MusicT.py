import discord, os, yt_dlp, subprocess
from Comp.Ids import CMusic
from discord.ext import commands



async def music(ctx, url: str, bot):
  print("downloading")
  await ctx.response.send_message('Cargando...')
  
  ydl_opts = {'quiet': True}
  
  with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=False)
    song_title = info.get('title', 'N/A')
  
  #obtener ruta
  directorio_func = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  ruta_comp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffmpeg/bin/ffmpeg.exe')


  # Descarga la música utilizando yt-dlp
  file_name = (f'Func/{song_title}')
  ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': file_name,
    'ffmpeg_location': ruta_comp,
    'postprocessors': [{
      'key': 'FFmpegExtractAudio',
      'preferredcodec': 'mp3',
      'preferredquality': '192'
    }],
    'quiet': True,
    'no_warnings': True
  }
  #If not work try pip install --upgrade yt-dlp in terminal
  try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      ydl.download([url])
  except:
    await ctx.edit_original_response(content='Retry in 2 minutes.')
    subprocess.run(['pip install --upgrade yt-dlp'], capture_output=True, text=True, shell=True)
    await bot.close()
    
  # Sube el archivo a un canal específico
  channel = bot.get_channel(CMusic)
  await ctx.edit_original_response(content='Subiendo...')
  await channel.send(file=discord.File(f'{file_name}.mp3'))
  await ctx.delete_original_response()
  os.remove(f'{file_name}.mp3')
  print('Done')



async def play(ctx, url, bot):
  voice_channel = bot.get_channel(1085953141276676169)
  await voice_channel.connect()
  with yt_dlp.YoutubeDL({'format': 'bestaudio'}) as ydl:
    info = ydl.extract_info(url, download=False)
    URL = info['formats'][0]['url']
    voice_client = ctx.guild.voice_client
    voice_client.play(discord.FFmpegPCMAudio(URL))


async def voice_disconnect(ctx, bot):
  if ctx.guild.voice_client:
    await ctx.guild.voice_client.disconnect()
    await ctx.response.send_message('Disconnected')
  else:
    await ctx.response.send_message('Not in voice channel')



class MenuVolume(discord.ui.View):
  def __init__(self, ctx, bot, rmenu):
    super().__init__()
    self.ctx = ctx
    self.RMenu = rmenu
    max_volume = 3
    num_buttons = 10
    self.value = 0
    step = max_volume / num_buttons
    for i in range(num_buttons):
      self.value = round((i+1)*step, 2)
      button = discord.ui.Button(label=str(self.value))
      button.callback = self.callback_volume(self.ctx, level=self.value)
      self.add_item(button)


  def callback_volume(self, ctx, level):
    async def volume(ctx):
      if self.RMenu:
        await self.RMenu.message.delete()
      await ctx.response.send_message('Volume changed to ' + str(level))
      self.RMenu.volume_val = level
      self.RMenu.message = await ctx.original_response()
    return volume



class MenuSound(discord.ui.View):
  def __init__(self, ctx, bot, rmenu):
    super().__init__()
    self.ctx = ctx
    self.RMenu = rmenu
    for file in os.listdir('Sounds'):
      sound = os.path.splitext(str(file))
      if sound[1] != '.exe':
        button = discord.ui.Button(label=str(sound[0]))
        button.callback = self.callback_sound(ctx, sound=str(sound[0]))
        self.add_item(button)

  def callback_sound(self, ctx, sound):
    async def d_sound(ctx):
      if not ctx.guild.voice_client.is_playing():
        await self.RMenu.messager(ctx, sound)
        source = discord.FFmpegPCMAudio(executable='Sounds/ffmpeg.exe', 
                                        source='Sounds/'+sound+'.mp3',
                                        options=f'-af "volume={self.RMenu.volume_val}"')
        self.RMenu.ctx.guild.voice_client.play(source)
      else:
        await self.RMenu.messager(ctx, message='Wait to finish playing')
    return d_sound



class Menu(discord.ui.View):
  def __init__(self, ctx, bot):
    super().__init__()
    self.ctx = ctx
    self.message = None
    self.volume_val = 1
    self.bot = bot
    self.soundmenu = None

  async def messager(self, ctx, message):
    if self.message:
      await self.message.delete()
      self.message = None
    await ctx.response.send_message(message)
    self.message = await ctx.original_response()
  
  async def stop(self, ctx):
    await self.messager(ctx, message='Sound stopped' if ctx.guild.voice_client else 'Nothing to stop')
    if ctx.guild.voice_client:
      await self.ctx.guild.voice_client.stop()

  async def volume(self, ctx):
    if self.message:
      await self.message.delete()
      self.message = None
    await ctx.response.send_message('Volume Menu', view=MenuVolume(ctx=ctx, bot=self.bot, rmenu=self))
    self.message = await ctx.original_response()
      
  async def sounds(self, ctx):
    if not self.soundmenu:
      await ctx.response.send_message('Sounds Menu', view=MenuSound(ctx=ctx, bot=self.bot, rmenu=self))
      self.soundmenu = await ctx.original_response()
    else:
      await self.soundmenu.delete()
      self.soundmenu = None
      await self.sounds(ctx)


  @discord.ui.button(label="Stop", style=discord.ButtonStyle.grey)
  async def menu1(self, ctx: discord.Interaction, button: discord.ui.Button):
    await self.stop(ctx)

  @discord.ui.button(label="Volume", style=discord.ButtonStyle.grey)
  async def menu2(self, ctx: discord.Interaction, button: discord.ui.Button):
    await self.volume(ctx)

  @discord.ui.button(label="Sounds", style=discord.ButtonStyle.grey)
  async def menu3(self, ctx: discord.Interaction, button: discord.ui.Button):
    await self.sounds(ctx)



async def ef(ctx, bot):
  if not ctx.guild.voice_client:
    await ctx.channel.connect()
  await ctx.response.send_message('Sound Menu', view=Menu(ctx, bot))  