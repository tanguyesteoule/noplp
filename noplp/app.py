from flask import Flask, render_template, send_from_directory, request, url_for, redirect
import random
import re
import pandas as pd
import os.path

app = Flask(__name__)
df_lyrics = pd.read_csv('data/lyrics.csv')
df_lyrics = df_lyrics.fillna('')
df_songs = pd.read_csv('data/songs.csv')


@app.route('/')
def index():
    id_song = random.choice(df_songs['id_song'].values)
    # id_song = 0
    song = df_songs.iloc[id_song]
    name = f"{song['artist']} - {song['title']}"
    lyrics_song = df_lyrics[df_lyrics['id_song'] == id_song].reset_index(drop=True)
    first_possible = lyrics_song[lyrics_song['type'] == 'possible'].index
    if len(first_possible) != 0:
        first_possible = first_possible[0]
    else:
        first_possible = len(lyrics_song)

    # Keep only real lyrics and drop duplicates (chorus)
    lyrics_song_sub_raw = lyrics_song.drop_duplicates(subset=['lyrics'], keep=False)

    # lyrics_song_sub = lyrics_song_sub.dropna()
    lyrics_song_sub = lyrics_song_sub_raw.loc[4:first_possible - 1].dropna()
    degraded = False
    if len(lyrics_song_sub) == 0:
        lyrics_song_sub = lyrics_song_sub_raw.dropna()
        degraded = True

    choice = random.choice(lyrics_song_sub.index)

    lyrics_before = list(lyrics_song.loc[:choice - 1]['lyrics'].values)

    answer = lyrics_song_sub.loc[choice]['lyrics'].lower()
    answer = re.findall(r"[\w']+", answer)

    return render_template('index.html', id_song=id_song, name=name, lyrics_before=lyrics_before, answer=answer,
                           len=len(answer), degraded=degraded)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT'))
