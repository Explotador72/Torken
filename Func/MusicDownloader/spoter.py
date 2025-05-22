import os, time, glob, shutil, spotipy, requests, threading, subprocess, zipfile, signal, asyncio
from Comp.Ids import CMusic
from flask import Flask, send_file, make_response
from spotipy.oauth2 import SpotifyOAuth
from concurrent.futures import ThreadPoolExecutor
from yt_dlp import YoutubeDL
from urllib.parse import quote
from flask import request


# 1. Credenciales de tu app de Spotify
CLIENT_ID = '382cbaacee964b1f9bafdf14ab86f549'
CLIENT_SECRET = 'dd3837f246be4b25bda112828d5518a5'
REDIRECT_URI = 'https://www.google.com/?hl=es'  # Debe coincidir con el de tu app en Spotify
SCOPE = 'playlist-read-private playlist-read-collaborative'
REFRESH_TOKEN = 'AQA0uEKy1yOhrFvzEhHWiNpGWIBfCkash3VrRQSNgky7jJqojwSn-hZRnBRMPOtLiu7FZUJtbYuRdAH5CLDEcF01ZDMu1R5a74QqdzzUmRwA7N2s4yzfFamJVz-L6DqEBws'


# 2. Autenticación usando Spotipy y OAuth
auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE)
token_info = auth_manager.refresh_access_token(REFRESH_TOKEN)
access_token = token_info['access_token']
sp = spotipy.Spotify(auth=access_token)
ngrok_process = None
download_completed = None

path_downloads = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Downloads_playlists/')


def normalize_str(string):
    # Elimina caracteres inválidos para nombres de archivo
    return string.translate(str.maketrans('\\/:*?"<>|', "__       "))


def download_from_youtube(track, playlist_name):
    track_name = normalize_str(track["name"]).strip()
    artist_name = normalize_str(", ".join([a["name"] for a in track["artists"]]))
    download_path = f"{path_downloads}{playlist_name}"

    if any(glob.glob(os.path.join(download_path, f"*{track_name}*.mp3"))):
        return

    ydl_opts = {
        'quiet': True,
        "skip_download": True,
        "force_generic_extractor": True,
        'noplaylist': True,
        'no-warnings': True  }
          
    with YoutubeDL({**ydl_opts, 'extract_flat': True}) as ydl:
        try:
            search_results = ydl.extract_info(f"ytsearch3:{track_name} {artist_name}",download=False).get('entries', [])
            
            if not search_results:
                print(f"No se encontró: {track_name} - {artist_name}")
                return
                
            track_duration = track['duration_ms'] // 1000
            best_match = min(search_results, key=lambda x: abs(x.get('duration', 0) - track_duration))
            best_url = best_match['url']

        except Exception as e:
            print(f"Error en búsqueda: {str(e)}")
            return
                    
    print(f"Descargando: {track_name} - {artist_name}\nURL: {best_url}")
    
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{download_path}/{artist_name} - {track_name}.%(ext)s",
        "ignoreerrors": True,
        "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            }],
            'quiet': True,
            'no_warnings': True
    }

    for attempt in range(2):
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([best_url])
                normalize_audio(f"{download_path}/{artist_name} - {track_name}.mp3")
                break
        except Exception as e:
            print(e)
            time.sleep(.5)


def normalize_audio(input_file):
    output_file = input_file.replace(".mp3", "_normalized.mp3")

    ffmpeg_cmd = [
        "ffmpeg",
        "-loglevel", "quiet",
        "-i", input_file,
        "-af", "loudnorm=I=-16:LRA=11:TP=-1.5",
        "-ar", "44100",         # Sample rate (opcional)
        "-b:a", "320k",         # Bitrate de audio (opcional)
        output_file
    ]
    subprocess.run(ffmpeg_cmd, check=True)
    os.remove(input_file)
    os.rename(output_file, input_file)

    print("Audio normalizado correctamente.")


print("\nTus playlists:")
def get_playlist(playlist_url):
    playlist_id = playlist_url.split("/")[-1].split("?")[0]
    playlist = sp.playlist(playlist_id)
    playlist_name = normalize_str(playlist['name']).strip()

    results = sp.playlist_items(playlist_id, limit=100, offset=0)
    all_tracks = results['items']

    while results['next']:
        results = sp.next(results)
        all_tracks.extend(results['items'])

    with ThreadPoolExecutor(max_workers=10) as executor:
        for item in all_tracks:
            executor.submit(download_from_youtube, item['track'], playlist_name)

    zip_path = f'{path_downloads}/{playlist_name}.zip'
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, dirs, files in os.walk(f'{path_downloads}/{playlist_name}'):
            for file in files:
                zipf.write(os.path.join(root, file), file)

    shutil.rmtree(f"{path_downloads}/{playlist_name}")
    return zip_path


async def upload_file(file_path, ctx):
    app = Flask(__name__)
    port = 5000

    result = {
        'public_url': None, 'download_event': asyncio.Event(), 'shutdown_event': asyncio.Event()}

    @app.route('/download')
    def download_file():
        response = make_response(send_file(file_path, as_attachment=True))
        response.headers["ngrok-skip-browser-warning"] = "true"
        return response

    def run_server():
        app.run(port=port)

    async def start_ngrok():
        ngrok_process = subprocess.Popen(["ngrok", "http", str(port)],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        await asyncio.sleep(2)
        try:
            # Espera a que el túnel se cree
            tunnels = requests.get("http://localhost:4040/api/tunnels").json()
            result['public_url'] = tunnels["tunnels"][0]["public_url"]
            print(f"🔗 URL: {result['public_url']}/download")
            await ctx.edit_original_response(content=f"Descarga lista: {result['public_url']}/download")
            await asyncio.wait_for(result['shutdown_event'].wait(), timeout=7200)
        except asyncio.TimeoutError:
            print("\n⏰ Tiempo límite alcanzado. Cerrando ngrok...")
            if os.name == 'nt':  # Windows
                subprocess.run(["TASKKILL", "/F", "/PID", str(ngrok_process.pid), "/T"])
            else:  # Unix-like
                os.kill(ngrok_process.pid, signal.SIGTERM)

    flask_thread = threading.Thread(target=run_server, daemon=True)
    flask_thread.start()

    await start_ngrok()
    os.remove(file_path)
    return


async def set_up(ctx, url, bot):
    channel = bot.get_channel(CMusic)
    await ctx.response.send_message('Descargando...')
    zip_file = get_playlist(url)
    await upload_file(zip_file, ctx)