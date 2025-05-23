import GenWeb
import Commands
import threading

# Inicia el bot de Discord en un hilo de ejecución separado
bot_thread = threading.Thread(target=Commands.bot.run, args=(Commands.TOKEN,))
bot_thread.start()

# Inicia el servidor web en un hilo de ejecución separado
web_thread = threading.Thread(target=GenWeb.run_web_server)
web_thread.start()

# Espera a que ambos hilos de ejecución finalicen
web_thread.join()
bot_thread.join()