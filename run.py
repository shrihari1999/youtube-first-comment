import pickle, ciso8601, time, urllib.request
from apiclient.discovery import build

BUCKET_NAME = 'complymate'
TOKEN_ID = 1

filename = f'token_{TOKEN_ID}.pkl'
urllib.request.urlretrieve(f'https://{BUCKET_NAME}.s3.amazonaws.com/youtube/pickles/{filename}', filename)
credentials = pickle.load(open(filename, 'rb'))
service = build('youtube', 'v3', credentials=credentials)

config_filename = 'config.txt'
urllib.request.urlretrieve(f'https://{BUCKET_NAME}.s3.amazonaws.com/youtube/{config_filename}', config_filename)
uploads_list_id, threshold_datetime = [line.decode('utf-8').strip() for line in open(config_filename, 'rb').readlines()]

while True:
    playlist_items_response = service.playlistItems().list(
        playlistId=uploads_list_id,
        part="snippet",
        fields='items(snippet(publishedAt,resourceId(videoId)))',
        maxResults=1
    ).execute()

    playlist_item_snippet = playlist_items_response['items'][0]['snippet']
    if ciso8601.parse_datetime(playlist_item_snippet['publishedAt']) > ciso8601.parse_datetime(threshold_datetime):
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
