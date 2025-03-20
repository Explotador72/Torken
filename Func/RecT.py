import asyncio
import pytz
import pickle
import os
from Comp.Ids import CRem
from datetime import datetime

events = []
archivo = './Comp/Nexo/SVariable.pickle'


# Definir función para enviar mensaje en un momento específico
async def send_announcement(text, fecha_final, bot, Tim_rem, user):
  indice = await add_event(text, fecha_final, user)
  if Tim_rem > 0:
    channel = await bot.fetch_channel(CRem)
    await asyncio.sleep(Tim_rem)
    await channel.send(f'{text} {user}')
    events.pop(indice)
    with open(archivo, 'wb') as f:
      pickle.dump(events, f)
  else:
    print("Negative time")
    events.pop(indice)
    print("poped event", indice)
    with open(archivo, 'wb') as f:
      pickle.dump(events, f)
    return


#Guardar
async def add_event(text, fecha_final, user):
  global events
  if os.stat(archivo).st_size != 0:
    with open(archivo, 'rb') as f:
      events = pickle.load(f)
  events.append((text, fecha_final, user))
  indice = events.index((text, fecha_final, user))
  # Guardar la variable en un archivo
  with open(archivo, 'wb') as f:
    pickle.dump(events, f)
  return indice


#Cargar
async def charge_event(bot):
  if os.stat(archivo).st_size != 0:
    global events
    with open(archivo, 'rb') as f:
      events = pickle.load(f)
      count = 0
      for item in events:
        print("item:", item)
        text, fecha_final, user = item
        zona_horaria = pytz.timezone('Europe/Madrid')
        fecha_inicial = datetime.now(zona_horaria)
        fecha_inicial = fecha_inicial.strftime('%m:%d:%H:%M:%S')

        mesI, diaI, horaI, minutosI, segundosI = map(int, fecha_inicial.split(":"))
        timeI = float(mesI * 2592000 + diaI * 86400 + horaI * 3600 + minutosI * 60 + segundosI) * 0.0001

        mesF, diaF, horaF, minutosF, segundosF = map(int, fecha_final.split(":"))
        timeF = float(mesF * 2592000 + diaI * 86400 + horaF * 3600 + minutosF * 60 + segundosF) * 0.0001

        Tim_rem = (timeF - timeI) / 0.0001
        indice = count
        count += 1
        asyncio.get_event_loop().create_task(
          send_announcement_initial(text, fecha_final, user, bot, Tim_rem, indice, events))
        



# Definir evento cuando el bot recibe un mensaje
async def rem(ctx, message, hour, minutes, day, month, bot, user):
  # Separar los argumentos del mensaje
  print("Program")
  # Crear objeto datetime con la fecha y hora especificadas
  zona_horaria = pytz.timezone('Europe/Madrid')
  fecha_inicial = datetime.now(zona_horaria)
  if hour is None:
    hour = fecha_inicial.hour
  if day is None:
    day = fecha_inicial.day
  if month is None:
    month = fecha_inicial.month
  if user is None or not user:
    user = ctx.user.mention

  fecha_inicial = fecha_inicial.strftime('%m:%d:%H:%M:%S')
  fecha_final = datetime(2023, month, day, hour, minutes)
  fecha_final = fecha_final.strftime('%m:%d:%H:%M:%S')

  print(fecha_final)
  #Pasar a int
  mesI, diaI, horaI, minutosI, segundosI = map(int, fecha_inicial.split(":"))
  timeI = float(mesI * 2592000 + diaI * 86400 + horaI * 3600 + minutosI * 60 + segundosI) * 0.0001

  mesF, diaF, horaF, minutosF, segundosF = map(int, fecha_final.split(":"))
  timeF = float(mesF * 2592000 + diaF * 86400 + horaF * 3600 + minutosF * 60 + segundosF) * 0.0001

  Tim_rem = (timeF - timeI) / 0.0001
  mesF, diaF, horaF, minutosF, segundosF = int(Tim_rem // 2592000), int((Tim_rem % 2592000) // 86400), int((Tim_rem % 86400) // 3600), int((Tim_rem % 3600) // 60), round(((Tim_rem % 3600) % 60), 2)

  # Calcular el tiempo restante hasta la fecha y hora especificadas
  print(f"Time remain; {mesF}:{diaF}:{horaF}:{minutosF}:{segundosF}")
  await ctx.response.send_message("Fecha de início: " + str(fecha_inicial) +
                                  "\n" + "Fecha del evento: " +
                                  str(fecha_final) + "\n" +
                                  "Tiempo restante: " +
                                  f"{mesF}:{diaF}:{horaF}:{minutosF}:{segundosF}")

  text = message 
  # Iniciar temporizador para enviar el mensaje en la fecha y hora especificadas
  asyncio.get_event_loop().create_task(
    send_announcement(text, fecha_final, bot, Tim_rem, user))


#Variation al iniciar
async def send_announcement_initial(text, fecha_final, user, bot, Tim_rem, indice, events):
  channel = await bot.fetch_channel(CRem)
  if Tim_rem > 0:
    await asyncio.sleep(Tim_rem)
    await channel.send(f'{text} {user}')
    events.pop(indice)
    with open(archivo, 'wb') as f:
      pickle.dump(events, f)
  else:
    print("Negative time")
    await channel.send(f'Event timed out: \n Date: {fecha_final} \n message: {text}')
    events.pop(indice)
    print("poped event", indice)
    with open(archivo, 'wb') as f:
      pickle.dump(events, f)
    return