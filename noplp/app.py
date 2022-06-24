import json

from config import SECRET_KEY
from flask import Flask, render_template, session, redirect, request
import random
import re
import pandas as pd
import os.path
import sys

app = Flask(__name__)
app.secret_key = SECRET_KEY

df_lyrics = pd.read_csv('data/lyrics.csv')
df_lyrics = df_lyrics.fillna('')
df_songs = pd.read_csv('data/songs.csv')
df_prop = pd.read_csv('data/propositions.csv')


def init_session():
    limit = 1000
    list_songs_sel = sorted(df_prop.groupby('id_song').count().sort_values(by='points', ascending=False)[:limit].index.tolist())
    if 'list_songs_sel' not in session:
        session['list_songs_sel'] = json.dumps(list_songs_sel)


@app.route('/save_config/', methods=['POST'])
def save_config():
    session['list_songs_sel'] = request.json['selected_songs']
    return {}


@app.route('/config')
def config():
    init_session()
    list_songs_sel = json.loads(session['list_songs_sel'])
    list_songs_all = df_songs['id_song'].values.tolist()
    list_songs_all_name = (df_songs['artist'] + ' - ' + df_songs['title']).values.tolist()
    # session['list_songs_all'] = json.dumps(list_songs_all)

    return render_template('config.html', list_songs_sel=list_songs_sel, list_songs_all=list_songs_all,
                           list_songs_all_name=list_songs_all_name, len=len(list_songs_all))


@app.route('/')
def index():
    print(request.cookies.get('list_songs_sel'), file=sys.stderr)

    init_session()

    while True:
        list_songs_sel = json.loads(session['list_songs_sel'])
        id_song = random.choice(list_songs_sel)
        song = df_songs.iloc[id_song]
        name = f"{song['artist']} - {song['title']}"
        lyrics_song = df_lyrics[df_lyrics['id_song'] == id_song].reset_index(drop=True)
        first_possible = lyrics_song[lyrics_song['type'] == 'possible'].index
        if len(first_possible) != 0:
            first_possible = first_possible[0]
        else:
            first_possible = len(lyrics_song)

        try:
            # Keep only real lyrics and drop duplicates (chorus)
            lyrics_song_sub_raw = lyrics_song.drop_duplicates(subset=['lyrics'], keep=False)

            # Remove lyrics with parenthesis
            lyrics_song_sub_raw = lyrics_song_sub_raw[~lyrics_song_sub_raw['lyrics'].str.contains("\(")]

            # lyrics_song_sub = lyrics_song_sub.dropna()
            lyrics_song_sub = lyrics_song_sub_raw.loc[4:first_possible - 1].dropna()
            degraded = False
            if len(lyrics_song_sub) == 0:
                lyrics_song_sub = lyrics_song_sub_raw.dropna()
                degraded = True

            choice = random.choice(lyrics_song_sub.index[4:])

            lyrics_before = list(lyrics_song.loc[:choice - 1]['lyrics'].values)

            answer = lyrics_song_sub.loc[choice]['lyrics'].lower()
            answer = re.findall(r"[\w']+", answer)

            return render_template('index.html', id_song=id_song, name=name, lyrics_before=lyrics_before, answer=answer,
                                   len=len(answer), degraded=degraded, list_songs_sel=list_songs_sel)

        except IndexError:
            print(f'ERROR id_song {id_song}, {name}')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT'))
