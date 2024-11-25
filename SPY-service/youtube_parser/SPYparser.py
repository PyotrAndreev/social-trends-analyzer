import re
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import openai

API_KEY = "youtube_api_key"
OPENAI_API_KEY = "your_openai_api_key"
openai.api_key = "your_openai_api_key"

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
LINK_REGEX = r"https?://[^\s]+"


def analyze_html_with_chatgpt(html_content):
    try:
        chunk_size = 3000
        chunks = [html_content[i:i + chunk_size] for i in range(0, len(html_content), chunk_size)]

        responses = []
        for chunk in chunks:
            prompt = f"Я анализирую рекламные страницы. Вот HTML-код страницы: {chunk} Подскажи, какой бренд и продукт рекламируются на этой странице?"

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000
            )

            if 'choices' in response and len(response['choices']) > 0:
                content = response['choices'][0].get('message', {}).get('content', '')
                responses.append(content.strip())
            else:
                responses.append("Не удалось извлечь ответ.")

        full_response = " ".join(responses)
        return full_response
    except Exception as e:
        return f"Ошибка при запросе к OpenAI API: {e}"


def extract_company_from_url(url):
    try:
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            html_content = response.text

            analysis_result = analyze_html_with_chatgpt(html_content)
            return analysis_result, None
        else:
            return "Ошибка доступа", None
    except Exception as e:
        print(f"Ошибка при анализе ссылки {url}: {e}")
        return "Неизвестно", None


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
    except HttpError as e:
        print(f"Ошибка при доступе к YouTube API: {e}")
        return []
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")
        return []


def extract_channel_id(channel_url, youtube):
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
    return re.findall(LINK_REGEX, text)


def parse_advertisers(youtube, channel_url):
    advertisers = []
    video_ids = get_video_ids_from_channel(youtube, channel_url)
    for video_id in video_ids:
        description, top_comment = get_video_details(youtube, video_id)

        description_links = extract_links(description)
        comment_links = extract_links(top_comment)
        all_links = description_links + comment_links

        for link in all_links:
            brand, product = extract_company_from_url(link)
            advertisers.append({
                "video_id": video_id,
                "link": link,
                "brand": brand,
                "product": product
            })

    return advertisers
