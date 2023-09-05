import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
from googleapiclient.errors import HttpError

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def create_playlist(all_songs):
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secrets.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)
    
    #creating playlist
    playlist_title = "My New Playlist"
    playlist_description = "A playlist of my favorite songs"
    request = youtube.playlists().insert(
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
    
    try:
        
        playlist = youtube.playlists().insert(part="snippet,status", body=request).execute()
        playlist_id = playlist["id"]
        print(f"Created playlist: {playlist_title} (ID: {playlist_id})")

        # Add songs to the playlist
        for song_name in all_songs:
            search_response = youtube.search().list(q=song_name, type="video", part="id").execute()
            video_id = search_response["items"][0]["id"]["videoId"]
            youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {"kind": "youtube#video", "videoId": video_id},
                    }
                },
            ).execute()
            print(f"Added {song_name} to the playlist.")

    except HttpError as e:
        print(f"An error occurred: {e}")