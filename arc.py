import os
import time
import json
import pygame.mixer as mixer
from audio_metadata import load as load_metadata
from tinydb import TinyDB, Query
from uuid import uuid4
import threading
from tinydb import where

# --- Init ---
mixer.init()
mix = mixer.music

# --- Config ---
MUSIC_DIR = 'music/'
db = TinyDB("database.json")
Music = Query()
state = 'stopped'
current_track_index = 0

# --- Playback Controls ---
def play(music=None):
    global state, current_track_index
    if not music and db.all():
        music = db.all()[current_track_index]['music_name']
    if music:
        mix.load(os.path.join(MUSIC_DIR, music))
        mix.play()
        state = 'playing'

def playlist_handler(command,name=None):
    if command == 'create':
        db.insert({'playlist':name,'music':None})



def stop():
    global state
    mix.stop()
    state = 'stopped'

def pause():
    global state
    mix.pause()
    state = 'paused'

def resume():
    global state
    mix.unpause()
    state = 'playing'

def seek(seconds):
    global state
    mix.play(0, seconds)
    state = 'playing'

# --- Info ---
def get_info():
    if not db.all():
        return {"state": "no_tracks"}
    
    music = db.all()[current_track_index]['music_name']
    try:
        metadata = load_metadata(os.path.join(MUSIC_DIR, music))
        duration_secs = int(metadata['streaminfo']['duration'])
        pos_secs = mix.get_pos() // 1000

        # Format position
        pos_minutes, pos_seconds = divmod(pos_secs, 60)
        pos_formatted = f"{pos_minutes}:{pos_seconds:02d}"

        # Format duration
        dur_minutes, dur_seconds = divmod(duration_secs, 60)
        dur_formatted = f"{dur_minutes}:{dur_seconds:02d}"

        return {
            "duration": dur_formatted,
            "position": pos_formatted,
            "state": state,
            "music": music
        }
    except:
        return {"state": "error"}



# --- Playlist / DB ---
def update_playlist():
    existing_files = {entry['music_name'] for entry in db.all()}
    for filename in os.listdir(MUSIC_DIR):
        if filename.endswith('.mp3') and filename not in existing_files:
            try:
                metadata = load_metadata(os.path.join(MUSIC_DIR, filename))
                duration_secs = int(metadata['streaminfo']['duration'])

                dur_minutes, dur_seconds = divmod(duration_secs, 60)
                dur_formatted = f"{dur_minutes}:{dur_seconds:02d}"

                db.insert({
                    "music_name": filename,
                    "duration": dur_formatted
                })
            except:
                continue


def get_playlist():
    return db.all()

def next_track():
    global current_track_index
    current_track_index = (current_track_index + 1) % len(db)
    play()

def previous_track():
    global current_track_index
    current_track_index = (current_track_index - 1) % len(db)
    play()

