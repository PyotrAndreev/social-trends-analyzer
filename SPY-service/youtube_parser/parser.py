import re
import requests
import os
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from bs4 import BeautifulSoup
import chardet
import time

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")
BRANDFETCH_API_KEY = os.getenv("BRANDFETCH_API_KEY")
CAPTCHA_API_KEY = os.getenv("CAPTCHA_API_KEY")

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
BRANDFETCH_URL = "https://developers.brandfetch.com/dashboard/brand-search-api"

LINK_REGEX = r"https?://[^\s]+"


def get_brand_info_from_brandfetch(url):
    """Получение информации о бренде через Brandfetch API."""
    headers = {
        "Authorization": f"Bearer {BRANDFETCH_API_KEY}"
    }

    try:
        response = requests.get(f"{BRANDFETCH_URL}?url={url}", headers=headers)
        if response.status_code == 200:
            brand_data = response.json()
            if brand_data.get('domain', None):
                # Вернем информацию о бренде, если бренд найден
                return brand_data.get('name'), brand_data.get('logo')
            else:
                print(f"Бренд не найден для ссылки: {url}")
                return None, None
        else:
            print(f"Ошибка при запросе Brandfetch: {response.text}")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к Brandfetch API: {e}")
        return None, None


def solve_captcha_with_2captcha(captcha_url):
    """Решение капчи через 2Captcha."""
    try:
        session = requests.Session()
        response = session.post(
            "http://2captcha.com/in.php",
            data={
                "key": CAPTCHA_API_KEY,
                "method": "userrecaptcha",
                "googlekey": "SITE_KEY",  # Укажите SITE_KEY из страницы
                "pageurl": captcha_url,
                "json": 1,
            },
        )
        captcha_id = response.json().get("request")
        # Ждем решения
        for _ in range(30):  # Максимум 30 попыток
            time.sleep(5)
            result = session.get(
                "http://2captcha.com/res.php",
                params={
                    "key": CAPTCHA_API_KEY,
                    "action": "get",
                    "id": captcha_id,
                    "json": 1,
                },
            )
            if result.json().get("status") == 1:
                return result.json().get("request")
        return None
    except Exception as e:
        print(f"Ошибка при решении капчи: {e}")
        return None


def expand_short_url(url):
    """Разворачивает сокращенные ссылки."""
    try:
        response = requests.head(url, allow_redirects=True)
        return response.url
    except Exception as e:
        print(f"Ошибка при разворачивании ссылки {url}: {e}")
        return url


def extract_utm_parameters(url):
    """Извлекает UTM-метки из ссылки."""
    parsed_url = urlparse(url)
    utm_params = parse_qs(parsed_url.query)
    utm_data = {key: value[0] for key, value in utm_params.items() if key.startswith('utm_')}
    return utm_data


def extract_company_from_url(url):
    """Извлекает бренд и продукт из содержимого HTML-страницы через Brandfetch."""
    brand, logo = get_brand_info_from_brandfetch(url)

    if brand:
        # Если бренд найден, то можно перейти к парсингу HTML для извлечения продукта
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=20)
            if response.status_code == 403 and "captcha" in response.text.lower():
                print(f"Обнаружена капча на {url}")
                captcha_solution = solve_captcha_with_2captcha(url)
                if captcha_solution:
                    print(f"Капча решена: {captcha_solution}")
                    response = requests.get(url, headers=headers, timeout=20)
            if response.status_code == 200:
                detected_encoding = response.encoding if response.encoding else chardet.detect(response.content)[
                    'encoding']
                response.encoding = detected_encoding

                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')

                title = soup.title.string if soup.title else "Неизвестно"
                meta_tags = soup.find_all('meta')
                meta_description = next((meta['content'] for meta in meta_tags if meta.get('name') == 'description'),
                                        None)

                product = meta_description or title
                return brand, product  # Возвращаем бренд и продукт
            else:
                return "Ошибка доступа", None
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе URL {url}: {e}")
            return "Неизвестно", None
        except Exception as e:
            print(f"Общая ошибка для URL {url}: {e}")
            return "Неизвестно", None
    else:
        return "Неизвестно", None


def initialize_youtube_client(api_key):
    """Инициализация клиента YouTube API."""
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=api_key)


def get_video_ids_from_channel(youtube, channel_url):
    """Получение списка ID видео на канале."""
    try:
        channel_id = extract_channel_id(channel_url, youtube)
        response = youtube.search().list(
            part="id",
            channelId=channel_id,
            maxResults=50,
            type="video"
        ).execute()
        return [item["id"]["videoId"] for item in response.get("items", [])]
    except HttpError as e:
        print(f"Ошибка при доступе к YouTube API: {e}")
        return []
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")
        return []


def extract_channel_id(channel_url, youtube):
    """Извлечение ID канала из URL."""
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


def get_video_details(youtube, video_id):
    """Получение описания видео и закрепленного комментария."""
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
    except KeyError:
        return "", ""
    except HttpError as e:
        print(f"Ошибка при запросе данных видео {video_id}: {e}")
        return "", ""
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")
        return "", ""


def extract_links(text):
    """Извлечение ссылок из текста."""
    return re.findall(LINK_REGEX, text)


def parse_advertisers(youtube, channel_url):
    """Парсинг рекламодателей на канале."""
    advertisers = []
    video_ids = ['PpaA08xDrJI']  # Для примера, используем конкретное видео
    for video_id in video_ids:
        description, top_comment = get_video_details(youtube, video_id)
        all_links = extract_links(description) + extract_links(top_comment)

        for link in all_links:
            expanded_url = expand_short_url(link)
            utm_data = extract_utm_parameters(expanded_url)
            brand, product = extract_company_from_url(expanded_url)

            if brand != "Неизвестно":  # Если бренд найден
                advertisers.append({
                    "video_id": video_id,
                    "link": expanded_url,
                    "utm_data": utm_data,
                    "brand": brand,
                    "product": product
                })
            else:
                print(f"Бренд не найден для ссылки: {expanded_url}")
    return advertisers


def main():
    youtube = initialize_youtube_client(API_KEY)
    test_channel_url = 'https://www.youtube.com/@faib'
    try:
        advertisers = parse_advertisers(youtube, test_channel_url)
        for advertiser in advertisers:
            print(f"\nВидео ID: {advertiser['video_id']}")
            print("Ссылка:", advertiser["link"])
            print("UTM метки:", advertiser["utm_data"])
            print("Бренд:", advertiser["brand"])
            print("Продукт:", advertiser["product"])
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()
