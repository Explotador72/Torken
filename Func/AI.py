import requests
import json
import io
import os, sys
import base64
import discord
import pickle
import requests
import random
#import Func.BotInsta
from PIL import Image
from Comp.Ids import CAI

archivo = './Comp/Insta.log'
file_path = "./Comp/Nexo/Insta-log.pickle"
image_name = 'ai.png'
url_ai = None

post_list = []
base_hashtaghs = '#ia #ai #sdxl #stablediffusion #aiart #generativeart #dalle #midjourney #upscale #sailing #aiartcommunity #artificialintelligence #digitaldrawing #digitalpainting'

try:
  with open(file_path, 'rb') as f:
    post_list = pickle.load(f)
except:
  with open(file_path, 'wb') as f:
    pickle.dump(post_list, f)


async def Post_insta(ctx, bot, prompt, custom_hashtaghs, url_imgs):
  global post_list

  id = random.randint(1, 1000)
  
  mes = await ctx.response.send_message(f'{id}: {prompt} \n\n.\n.\n....\n{base_hashtaghs} {custom_hashtaghs}')

  url_imgs = url_imgs.split("___")
  post = [id, prompt, custom_hashtaghs, url_imgs, mes]
  post_list.append(post)

  # Crear registro
  log = f'{post}'

  # Guardar registro en un archivo
  with open(archivo, "a") as f:
    f.write(log + "\n")
  
  with open(file_path, 'wb') as f:
    pickle.dump(post_list, f)
    
  for url in url_imgs:
    embed = discord.Embed()
    embed.set_image(url=url)
    await ctx.channel.send(embed=embed)



async def Url_ai(ctx, bot, url):
  global url_ai, prompts_list
  url_ai = url
  response = requests.get(url_ai)
  if response.status_code == 200:
    await ctx.response.send_message('Set url')
  else:
    await ctx.response.send_message(
      'Incorrect url \n Be sure that colab \n has started the AI')


async def AIC(ctx, bot, url, prompt):
  global url_ai
  await ctx.response.send_message('Received, in process')
  if url:
    url_ai = url
    temp_url = url_ai + 'v1/generation/text-to-image'
  else:
    if url_ai:
      temp_url = url_ai + 'v1/generation/text-to-image'
    else:
      await ctx.edit_original_response(content='Not url added')

  prompts_list = prompt.split('//')
  for prompts in prompts_list:
    data = {
      'prompt': prompts,
    }
    if url_ai:
      headers = {'Content-Type': 'application/json'}
      response = requests.post(temp_url,
                               data=json.dumps(data),
                               headers=headers)

      if response.status_code == 200:

        # La respuesta contiene la imagen generada
        await ctx.edit_original_response(content='Image Created')

        r = response.json()

        image_txt = str(r[0]['base64'])
        image = Image.open(io.BytesIO(base64.b64decode(image_txt)))
        image.save(image_name)

        embed = discord.Embed(title='',
                              description=f'Prompt: {prompt}',
                              color=discord.Color.purple())

        channel = bot.get_channel(CAI)
        await channel.send(embed=embed, file=discord.File(image_name))
        os.remove(image_name)
        try:
          await ctx.delete_original_response()
        except:
          pass

      else:
        await ctx.edit_original_response('Error...')
        print('Error al acceder a la página web:', response.status_code)
    else:
      await ctx.edit_original_response('Invalid Url')
      print('Error al acceder a la página web:', response.status_code)
