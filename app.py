from flask import Flask, render_template, request
import csv
import math
import spotipy
import json
import os
import concurrent.futures
from spotipy.oauth2 import SpotifyClientCredentials
from ordenacao import counting_sort, radix_sort, merge_sort
from dotenv import load_dotenv


app = Flask(__name__)

load_dotenv()

CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager, retries=0)

def carregar_dados_musicas():
    musicas = []
    with open('data/spotify_data clean.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                track_id = str(row.get('track_id', '')).strip()
                if len(track_id) != 22:
                    continue
                row['track_id'] = track_id
                
                row['track_popularity'] = int(row['track_popularity'])
                row['artist_followers'] = int(row['artist_followers'])
                row['duration_sec'] = int(float(row['track_duration_min']) * 60)

                genero = str(row.get('artist_genres', '')).strip()
                row['artist_genres'] = genero if genero and genero.lower() != 'nan' else 'Desconhecido'
                
                musicas.append(row)
            except ValueError:
                continue
    return musicas

base_musicas = carregar_dados_musicas()
ITENS_POR_PAGINA = 30

ARQUIVO_CACHE = 'cache_capas.json'

if os.path.exists(ARQUIVO_CACHE):
    with open(ARQUIVO_CACHE, 'r', encoding='utf-8') as f:
        cache_capas = json.load(f)
else:
    cache_capas = {}

def salvar_cache():

    with open(ARQUIVO_CACHE, 'w', encoding='utf-8') as f:
        json.dump(cache_capas, f)

def buscar_uma_capa(musica):
    track_id = musica.get('track_id', '').strip()

    if track_id in cache_capas:
        musica['cover_url'] = cache_capas[track_id]
        return musica
    

    try:
        track_info = sp.track(track_id)
        if track_info and len(track_info['album']['images']) > 0:
            url = track_info['album']['images'][1]['url']
        else:
            url = 'https://placehold.co/300x300/282828/282828?text='
            
        cache_capas[track_id] = url 
        musica['cover_url'] = url
        
    except Exception:
        musica['cover_url'] = 'https://placehold.co/300x300/282828/282828?text='
        
    return musica

def adicionar_capas(lista_musicas):
    if not lista_musicas:
        return lista_musicas

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        list(executor.map(buscar_uma_capa, lista_musicas))

    salvar_cache() 
    return lista_musicas


@app.route('/')
def index():
    criterio_ordenacao = request.args.get('ordenar_por', 'nenhum')
    ordem = request.args.get('ordem', 'desc')
    pagina_atual = int(request.args.get('pagina', 1))

    musicas_processadas = base_musicas.copy()

    if criterio_ordenacao == 'popularidade':
        musicas_processadas = counting_sort(musicas_processadas, 'track_popularity')
    elif criterio_ordenacao == 'seguidores':
        musicas_processadas = radix_sort(musicas_processadas, 'artist_followers')
    elif criterio_ordenacao == 'duracao':
        musicas_processadas = radix_sort(musicas_processadas, 'duration_sec')
    elif criterio_ordenacao == 'nome_musica':
        musicas_processadas = merge_sort(musicas_processadas, 'track_name')
    elif criterio_ordenacao == 'nome_artista':
        musicas_processadas = merge_sort(musicas_processadas, 'artist_name')
    elif criterio_ordenacao == 'album':
        musicas_processadas = merge_sort(musicas_processadas, 'album_name')
    elif criterio_ordenacao == 'genero':
        musicas_processadas = merge_sort(musicas_processadas, 'artist_genres')

    if ordem == 'desc' and criterio_ordenacao != 'nenhum':
        musicas_processadas.reverse()

    total_musicas = len(musicas_processadas)
    total_paginas = math.ceil(total_musicas / ITENS_POR_PAGINA)
    
    if pagina_atual < 1: pagina_atual = 1
    if pagina_atual > total_paginas and total_paginas > 0: pagina_atual = total_paginas

    indice_inicio = (pagina_atual - 1) * ITENS_POR_PAGINA
    indice_fim = indice_inicio + ITENS_POR_PAGINA
    musicas_da_pagina = musicas_processadas[indice_inicio:indice_fim]

    musicas_com_capa = adicionar_capas(musicas_da_pagina)

    return render_template(
        'index.html',
        musicas=musicas_com_capa,
        pagina_atual=pagina_atual,
        total_paginas=total_paginas,
        ordenacao_atual=criterio_ordenacao,
        ordem_atual=ordem
    )

if __name__ == '__main__':
    app.run(debug=True)