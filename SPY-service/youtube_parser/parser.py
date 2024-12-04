import re
import requests
import os
from urllib.parse import urlparse, parse_qs
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
import chardet
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
LINK_REGEX = r"https?://[^\s]+"


def expand_short_url(url):
    try:
        response = requests.head(url, allow_redirects=True)
        return response.url
    except Exception as e:
        print(f"Ошибка при разворачивании ссылки {url}: {e}")
        return url


def extract_company_from_url(url):
    try:
        expanded_url = expand_short_url(url)
        parsed_url = urlparse(expanded_url)
        domain = parsed_url.netloc

        response = requests.get(expanded_url, timeout=10)
        if response.status_code == 200:
            detected_encoding = response.encoding if response.encoding else chardet.detect(response.content)['encoding']
            response.encoding = detected_encoding

            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')

            title = soup.title.string if soup.title else "Неизвестно"
            meta_description = next(
                (meta['content'] for meta in soup.find_all('meta') if meta.get('name') == 'description'), None)

            product = meta_description or title
            return domain, product
        else:
            return domain, None
    except Exception as e:
        print(f"Ошибка при извлечении данных из URL {url}: {e}")
        return "Неизвестно", None


def extract_utm_parameters(url):
    parsed_url = urlparse(url)
    utm_params = parse_qs(parsed_url.query)
    utm_data = {key: value[0] for key, value in utm_params.items() if key.startswith('utm_')}
    return utm_data


def initialize_youtube_client(api_key):
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=api_key)


def get_video_ids_from_channel(youtube, channel_url):
    try:
        channel_id = extract_channel_id(channel_url, youtube)
        response = youtube.search().list(
            part="id",
            channelId=channel_id,
            maxResults=50,
            type="video"
        ).execute()
        return [item["id"]["videoId"] for item in response.get("items", [])]
    except Exception as e:
        print(f"Ошибка при получении видео с канала: {e}")
        return []


def extract_channel_id(channel_url, youtube):
    try:
        if "channel/" in channel_url:
            return channel_url.split("channel/")[1].split("/")[0]
        elif "user/" in channel_url:
            username = channel_url.split("user/")[1].split("/")[0]
            response = youtube.channels().list(forUsername=username, part="id").execute()
            return response["items"][0]["id"]
        elif "@" in channel_url:
            handle = channel_url.split("@")[1].split("/")[0]
            response = youtube.search().list(part="snippet", q=handle, type="channel", maxResults=1).execute()
            return response["items"][0]["snippet"]["channelId"]
        else:
            raise ValueError("Не удалось извлечь channelId. Проверьте URL.")
    except Exception as e:
        print(f"Ошибка при извлечении channelId: {e}")
        raise


def get_video_details(youtube, video_id):
    try:
        video_response = youtube.videos().list(
            part="snippet",
            id=video_id
        ).execute()
        description = video_response["items"][0]["snippet"]["description"]

        comments_response = youtube.commentThreads().list(
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


def extract_links(text):
    return re.findall(LINK_REGEX, text)


def parse_advertisers(youtube, channel_url):
    advertisers = []
    video_ids = get_video_ids_from_channel(youtube, channel_url)

    for video_id in video_ids:
        description, top_comment = get_video_details(youtube, video_id)
        all_links = extract_links(description) + extract_links(top_comment)

        for link in all_links:
            expanded_url = expand_short_url(link)
            utm_data = extract_utm_parameters(expanded_url)
            brand, product = extract_company_from_url(expanded_url)
            advertisers.append({
                "video_id": video_id,
                "link": expanded_url,
                "utm_data": utm_data,
                "brand": brand,
                "product": product
            })

    return advertisers
