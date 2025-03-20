from playwright.sync_api import sync_playwright
from datetime import datetime
import os
import json
import time

# Configuración
CONFIG = {
    'browser_dir': './browser',
    'screenshot_dir': './screenshots',
    'headless': True,
    'width': 1280,
    'height': 720,
    'timeout': 30000,
    'login_timeout': 120000,
    'debug': False,
    'record': False,
    'dryrun': False,
    'email': os.getenv('EG_EMAIL'),
    'password': os.getenv('EG_PASSWORD'),
    'otp_key': os.getenv('EG_OTP_KEY'),
    'parental_pin': os.getenv('EG_PARENTAL_PIN')
}

# Rutas de archivos
DB_FILE = 'epic-games.json'
URL_CLAIM = 'https://store.epicgames.com/en-US/free-games'
URL_LOGIN = 'https://www.epicgames.com/id/login?lang=en-US&noHostRedirect=true&redirectUrl=' + URL_CLAIM

# Funciones de utilidad
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def log(message):
    print(f"{datetime.now()} - {message}")

def capture_screenshot(page, name):
    page.screenshot(path=os.path.join(CONFIG['screenshot_dir'], name))

# Función principal
def main():
    db = load_db()
    
    with sync_playwright() as p:
        browser = p.firefox.launch_persistent_context(
            user_data_dir=CONFIG['browser_dir'],
            headless=CONFIG['headless'],
            viewport={'width': CONFIG['width'], 'height': CONFIG['height']},
            args=[],
            locale='en-US'
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()

        # Iniciar sesión
        log('Iniciando sesión en Epic Games...')
        page.goto(URL_LOGIN)
        
        if CONFIG['email'] and CONFIG['password']:
            page.fill('#email', CONFIG['email'])
            page.fill('#password', CONFIG['password'])
            page.click('button[type="submit"]')
            # Manejar autenticación de dos factores
            if CONFIG['otp_key']:
                otp = authenticator.generate(CONFIG['otp_key'])
                page.fill('input[name="code-input-0"]', otp)
                page.click('button[type="submit"]')

        # Verificar si el usuario ha iniciado sesión
        page.goto(URL_CLAIM)
        if page.query_selector('egs-navigation[isloggedin="true"]') is None:
            log('No se pudo iniciar sesión, abortando.')
            return
        
        user = page.get_attribute('egs-navigation', 'displayname')
        if user not in db:
            db[user] = {}
        
        # Obtener juegos gratuitos
        log('Obteniendo juegos gratuitos...')
        games = page.query_selector_all('a:has(span:text("Free Now"))')
        game_urls = ['https://store.epicgames.com' + game.get_attribute('href') for game in games]

        for url in game_urls:
            page.goto(url)
            time.sleep(1)  # Esperar para asegurar carga completa de la página

            # Manejar compra del juego
            if page.query_selector('button:has-text("Get")'):
                page.click('button:has-text("Get")')
                time.sleep(1)  # Esperar para asegurar que se procese el click
                page.click('button:has-text("Place Order")')

                if page.query_selector('text=Thanks for your order!'):
                    log(f'Juego "{url}" reclamado con éxito.')
                else:
                    log(f'Error al reclamar "{url}".')
                    capture_screenshot(page, 'error_claiming_game.png')
            
        # Guardar cambios en la base de datos
        save_db(db)
        log('Proceso completado.')

if __name__ == '__main__':
    main()
