import pickle, ciso8601, time, urllib.request
from apiclient.discovery import build
from datetime import datetime, timezone

BUCKET_NAME = 'complymate'
TOKEN_ID = 1

filename = f'token_{TOKEN_ID}.pkl'
urllib.request.urlretrieve(f'https://{BUCKET_NAME}.s3.amazonaws.com/youtube/pickles/{filename}', filename)
credentials = pickle.load(open(filename, 'rb'))
service = build('youtube', 'v3', credentials=credentials)

upload_list_filename = 'upload_list_id.txt'
urllib.request.urlretrieve(f'https://{BUCKET_NAME}.s3.amazonaws.com/youtube/{upload_list_filename}', upload_list_filename)
uploads_list_id = open(upload_list_filename, 'rb').readline().decode('utf-8')

while True:
    playlist_items_response = service.playlistItems().list(
        playlistId=uploads_list_id,
        part="snippet",
        fields='items(snippet(publishedAt,resourceId(videoId)))',
        maxResults=1
    ).execute()

    playlist_item_snippet = playlist_items_response['items'][0]['snippet']
    if ciso8601.parse_datetime(playlist_item_snippet['publishedAt']) > datetime(2022, 8, 4, 19, 59, 59, tzinfo=timezone.utc):
        video_id = playlist_item_snippet['resourceId']['videoId']
        body = {
            "snippet": {
                "videoId": video_id,
                "topLevelComment": {
                    "snippet": {
                        "textOriginal": "First"
                    }
                }
            }
        }
        service.commentThreads().insert(part='snippet', body=body).execute()
        print(f'Posted comment from token id: {TOKEN_ID} on {video_id}')
        break
    time.sleep(1)
