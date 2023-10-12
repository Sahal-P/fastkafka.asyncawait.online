from fastapi import FastAPI
import requests
from aiohttp import ClientSession
from config.config import config
import json

app = FastAPI()

async def fetch_data_page(playlist_id, page_token=None):
    api_key = config["google_api_key"]
    url = "https://www.googleapis.com/youtube/v3/playlistItems"
    params = {"key": api_key, "playlistId": playlist_id, "part": "contentDetails",}
    if page_token is not None:
        params["pageToken"] = page_token
    
    async with ClientSession() as session:
        async with session.get(url, params=params) as response:
            response_data = await response.text()
            return json.loads(response_data)
        
async def summerize_video(video):
    video = video[0]
    return {
        "video_id": video["id"],
        "title": video["snippet"]["title"],
        "views": int(video["statistics"].get("viewCount", 0)),
        "likes": int(video["statistics"].get("likeCount", 0)),
        "comments": int(video["statistics"].get("commentCount", 0)),
    }
        
async def fetch_videos_page(video_id, page_token=None):
    api_key = config["google_api_key"]
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {"key": api_key, "id": video_id, "part": "snippet, statistics",}
    if page_token is not None:
        params["pageToken"] = page_token
    
    async with ClientSession() as session:
        async with session.get(url, params=params) as response:
            response_data = await response.text()
            return json.loads(response_data)

async def fetch_data(playlist_id, page_token=None):
    payload = await fetch_data_page(playlist_id, page_token)
    items = payload.get("items", [])
    
    next_page_token = payload.get("nextPageToken")
    
    if next_page_token is not None:
        items.extend(await fetch_data(playlist_id, next_page_token))
    return items


@app.get("/")
async def root():
    playlist_id = "PLot-Xpze53leU0Ec0VkBhnf4npMRFiNcB"
    playlist = await fetch_data(playlist_id)
    for item in playlist:
        video_id = item["contentDetails"]["videoId"]
        video =  await fetch_videos_page(video_id)
        print(await summerize_video(video['items']))
    return {"message": playlist}
