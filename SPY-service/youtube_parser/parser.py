import re

import chardet
import requests
from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from playwright.sync_api import sync_playwright
from fastapi import HTTPException
from datetime import datetime
from core.config import Settings
from database.db_API import DBAPI
from schemas.advertisement import AdvertisementCreate
from schemas.brand import BrandCreate
from schemas.channel import ChannelCreate
from schemas.product import ProductCreate
from schemas.video import VideoCreate

API_KEY = 'AIzaSyBcoVP46wSMBhqE56irLl2ejLclAG1d9QY'

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
LINK_REGEX = r"https?://[^\s]+"


def initialize_youtube_client(api_key):
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=api_key)


class YouTubeParser:
    youtube = initialize_youtube_client(API_KEY)

    @staticmethod
    def expand_short_url(url):
        try:
            response = requests.head(url, allow_redirects=True)
            return response.url
        except Exception as e:
            print(f"Ошибка при разворачивании ссылки {url}: {e}")
            return url

    @staticmethod
    def extract_company_from_url(url):
        try:
            expanded_url = YouTubeParser.expand_short_url(url)
            parsed_url = urlparse(expanded_url)
            domain = parsed_url.netloc

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=50000)
                title = page.evaluate("document.title")
                browser.close()
            return domain, title
        except Exception as e:
            print(f"Ошибка при извлечении данных из URL {url}: {e}")
            return "Неизвестно", "Неизвестно"

    @staticmethod
    def extract_utm_parameters(url):
        parsed_url = urlparse(url)
        utm_params = parse_qs(parsed_url.query)
        utm_data = {key: value[0] for key, value in utm_params.items() if key.startswith('utm_')}
        return utm_data

    @staticmethod
    def extract_video_ids_from_channel(channel_url):
        try:
            channel_id = YouTubeParser.extract_channel_id(channel_url)
            video_ids = []
            next_page_token = None

            while True:
                response = YouTubeParser.youtube.search().list(
                    part="id",
                    channelId=channel_id,
                    maxResults=50,
                    type="video",
                    pageToken=next_page_token
                ).execute()

                video_ids.extend(item["id"]["videoId"] for item in response.get("items", []))
                next_page_token = response.get("nextPageToken")
                if not next_page_token:
                    break
            return list(set(video_ids))
        except Exception as e:
            print(f"Ошибка при получении видео с канала: {e}")
            return []

    @staticmethod
    def extract_channel_id(channel_url):
        try:
            if "channel/" in channel_url:
                return channel_url.split("channel/")[1].split("/")[0]
            elif "user/" in channel_url:
                username = channel_url.split("user/")[1].split("/")[0]
                response = YouTubeParser.youtube.channels().list(forUsername=username, part="id").execute()
                return response["items"][0]["id"]
            elif "@" in channel_url:
                handle = channel_url.split("@")[1].split("/")[0]
                response = YouTubeParser.youtube.search().list(part="snippet", q=handle, type="channel",
                                                               maxResults=1).execute()
                return response["items"][0]["snippet"]["channelId"]
            else:
                raise ValueError("Не удалось извлечь channelId. Проверьте URL.")
        except Exception as e:
            print(f"Ошибка при извлечении channelId: {e}")
            raise

    @staticmethod
    def get_video_details(video_id):
        try:
            video_response = YouTubeParser.youtube.videos().list(
                part="snippet",
                id=video_id
            ).execute()
            description = video_response["items"][0]["snippet"]["description"]

            comments_response = YouTubeParser.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=1,
                order="relevance"
            ).execute()
            top_comment = comments_response["items"][0]["snippet"]["topLevelComment"]["snippet"]["textDisplay"]

            return description, top_comment
        except Exception as e:
            print(f"Ошибка при получении данных видео {video_id}: {e}")
            return "", ""

    @staticmethod
    def extract_links(text):
        return re.findall(LINK_REGEX, text)

    @staticmethod
    def extract_channel_name(channel_url):
        base_url = "https://www.googleapis.com/youtube/v3/channels"
        params = {
            "part": "snippet",
            "id": YouTubeParser.extract_channel_id(channel_url),
            "key": API_KEY
        }

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()

            if "items" in data and len(data["items"]) > 0:
                channel_name = data["items"][0]["snippet"]["title"]
                return channel_name
            else:
                return "Канал с указанным ID не найден."
        except requests.exceptions.RequestException as e:
            return f"Ошибка при выполнении запроса: {e}"

    @staticmethod
    def extract_video_title(video_id):
        base_url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "snippet",
            "id": video_id,
            "key": API_KEY
        }

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()

            if "items" in data and len(data["items"]) > 0:
                video_title = data["items"][0]["snippet"]["title"]
                return video_title
            else:
                return "Видео с указанным ID не найдено."
        except requests.exceptions.RequestException as e:
            return f"Ошибка при выполнении запроса: {e}"

    @staticmethod
    def extract_video_publish_date(video_id):
        base_url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "snippet",
            "id": video_id,
            "key": API_KEY
        }

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()

            if "items" in data and len(data["items"]) > 0:
                publish_date_str = data["items"][0]["snippet"]["publishedAt"]
                publish_date = datetime.fromisoformat(publish_date_str.replace("Z", "+00:00"))
                return publish_date
            else:
                return "Видео с указанным ID не найдено."
        except requests.exceptions.RequestException as e:
            return f"Ошибка при выполнении запроса: {e}"

    @staticmethod
    def parse_channel(channel_url: str):
        try:
            with DBAPI() as db_api:
                channel_id = YouTubeParser.extract_channel_id(channel_url)
                channel_name = YouTubeParser.extract_channel_name(channel_url)
                db_channel = db_api.get_channel(channel_id)
                if not db_channel:
                    channel = ChannelCreate(
                        id=channel_id,
                        name=channel_name,
                        last_update=datetime.now()
                    )
                    db_channel = db_api.create_channel(channel)
                else:
                    db_channel.last_update = datetime.now()

                video_ids = YouTubeParser.extract_video_ids_from_channel(channel_url)
                for video_id in video_ids:
                    db_video = db_api.get_video(video_id)
                    if not db_video:
                        video = VideoCreate(
                            id=video_id,
                            title=YouTubeParser.extract_video_title(video_id),
                            published_at=YouTubeParser.extract_video_publish_date(video_id),
                            channel_id=db_channel.id,
                            last_update=datetime.now()
                        )
                        db_video = db_api.create_video(video)

                        description, top_comment = YouTubeParser.get_video_details(video_id)
                        all_links = YouTubeParser.extract_links(description) + YouTubeParser.extract_links(top_comment)
                        ignore = ['instagram', 'youtube', 'telegram', 'twitch', 'tiktok', 't.me']
                        for link in all_links:
                            expanded_url = YouTubeParser.expand_short_url(link)
                            if ('instagram' in expanded_url) or ('youtube' in expanded_url) or (
                                    'telegram' in expanded_url) or ('twitch' in expanded_url) or (
                                    'tiktok' in expanded_url) or ('t.me' in expanded_url):
                                continue
                            utm_data = YouTubeParser.extract_utm_parameters(expanded_url)
                            brand_name, product_name = YouTubeParser.extract_company_from_url(expanded_url)

                            db_brand = db_api.get_brand(brand_name)

                            if not db_brand and not (brand_name == 'Неизвестно'):
                                brand = BrandCreate(
                                    name=brand_name,
                                    last_update=datetime.now()
                                )
                                db_brand = db_api.create_brand(brand)
                            elif db_brand:
                                db_brand.last_update = datetime.now()

                            db_product = db_api.get_product(product_name)
                            if not db_product and brand_name != 'Неизвестно' and product_name != 'Неизвестно':
                                product = ProductCreate(
                                    name=product_name,
                                    brand_name=db_brand.name,
                                    last_update=datetime.now()
                                )
                                db_product = db_api.create_product(product)

                                db_advertisement = db_api.get_advertisement(expanded_url)
                                if not db_advertisement:
                                    advertisement = AdvertisementCreate(
                                        video_id=db_video.id,
                                        product_name=db_product.name,
                                        expanded_link=expanded_url,
                                        short_link=link,
                                        utm_tags=utm_data,
                                        last_update=datetime.now()
                                    )
                                    db_advertisement = db_api.create_advertisement(advertisement)
                                elif db_product:
                                    db_product.last_update = datetime.now()

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
