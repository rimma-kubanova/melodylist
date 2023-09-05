from flask import Flask, request, redirect, url_for, session, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import os
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import requests
import pywhatkit
import google_auth_oauthlib.flow
import googleapiclient.discovery
from googleapiclient.errors import HttpError
import re

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

app = Flask(__name__)

app.secret_key = "12345678"
app.config['SESSION_COOKIE_NAME'] = 'Rimmas Cookie'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///musics.db'
TOKEN_INFO = 'token_info' 
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "client_secrets.json"


flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
credentials = flow.run_console()
    

youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)
    

@app.route('/')
def login():
    sp_oauth=create_spotify_oauth()
    auth_url=sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code =request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('getTracks', _external=True))


@app.route('/getTracks')
def getTracks():
    try:
        token_info = get_token()
    except:
        print('user not logged in')
        return redirect(url_for('login', _external=False))
    sp = spotipy.Spotify(auth=token_info['access_token'])
    all_songs = []

    items = sp.current_user_saved_tracks(limit=10)['items']
    for idx, item in enumerate(items):
        track = item['track']
        val = track['name'] + " - " + track['artists'][0]['name']+' '+ 'instrumental'
        all_songs += [val]
    
    print(all_songs)
    song_urls = create_url_video(all_songs)
    create_youtube_playlist(song_urls)
    return redirect(url_for('createPlaylist'))


@app.route('/createPlaylist', methods=['GET'])
def createPlaylist():
    return 'created playlist'

def create_url_video(all_songs):
    urls=[]
    for song in all_songs:
        print('processing song', song)
        song_url = pywhatkit.playonyt(song, open_video=False)
        url_video = requests.get(song_url).url
        match = re.search(r'v=([A-Za-z0-9_-]+)', url_video)
        urls.append(match.group(1))
    return urls
    
def create_youtube_playlist(songs):
    
    #creating playlist
    playlist_title = "My New hi Playlist"
    playlist_description = "A playlist of my favorite songs"
    request_body = youtube.playlists().insert(
        part="snippet,status",
        body={
          "snippet": {
            "title": playlist_title,
            "description": playlist_description,
            "tags": [
              "sample playlist",
              "API call"
            ],
            "defaultLanguage": "en"
          }
        }
    )
    response = request_body.execute()
    print(response)
    playlist_id = response["id"]

    try:
        for song in songs:
            youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {"kind": "youtube#video", "videoId": song},
                    }
                },
            ).execute()
        return {"message": "Playlist created successfully!"}
    
    except HttpError as e:
        print(f"An error occurred: {e}")
        
def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise 'exception'
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if(is_expired):
        sp_oauth=create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info

clientID = 'cbdf0c481b20456ea76559644c246cc7'
clientSecret ='ecfae9e7b6f04140b98f4323f7472952'

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=clientID,
        client_secret=clientSecret,
        redirect_uri=url_for('redirectPage', _external=True),
        scope='user-library-read',
    )
