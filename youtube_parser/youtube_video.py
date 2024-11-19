import json
import re
import os
from youtube_resource import YouTubeResource
from brands import BRANDS
from googleapiclient.errors import HttpError


class YouTubeVideo(YouTubeResource):
    def __init__(self, youtube, resource_id):
        super().__init__(youtube, resource_id)
        try:
            self.metadata = self._fetch_metadata()
        except HttpError as e:
            raise ValueError(f"Ошибка при запросе метаданных видео: {e}")
        except Exception as e:
            raise ValueError(f"Не удалось инициализировать видео: {e}")

    def _fetch_metadata(self):
        try:
            request = self.youtube.videos().list(part="snippet,statistics", id=self.resource_id)
            response = request.execute()
            if not response['items']:
                raise ValueError("Видео не найдено.")
            video_info = response['items'][0]
            return {
                "title": video_info['snippet']['title'],
                "description": video_info['snippet']['description'],
                "tags": video_info['snippet'].get('tags', []),
                "published_at": video_info['snippet']['publishedAt'],
                "view_count": int(video_info['statistics'].get('viewCount', 0)),
                "like_count": int(video_info['statistics'].get('likeCount', 0)),
                "comment_count": int(video_info['statistics'].get('commentCount', 0))
            }
        except HttpError as e:
            raise ValueError(f"Ошибка при запросе видео: {e}")
        except KeyError as e:
            raise ValueError(f"Отсутствуют ожидаемые данные: {e}")
        except Exception as e:
            raise ValueError(f"Произошла ошибка при получении метаданных: {e}")

    def extract_links(self, text):
        if not text:
            return []
        try:
            return re.findall(r'https?://[^\s]+', text)
        except Exception as e:
            raise ValueError(f"Ошибка при извлечении ссылок: {e}")

    def identify_brand(self, link):
        try:
            for brand, keywords in BRANDS.items():
                for keyword in keywords:
                    if keyword.lower() in link.lower():
                        return brand
            return None
        except Exception as e:
            raise ValueError(f"Ошибка при определении бренда: {e}")

    def detect_brand(self, text):
        try:
            detected_brands = []
            for brand, keywords in BRANDS.items():
                if any(keyword in text.lower() for keyword in keywords):
                    detected_brands.append(brand)
            return detected_brands
        except Exception as e:
            raise ValueError(f"Ошибка при обнаружении брендов: {e}")

    def get_pinned_comment(self):
        try:
            comments = self.get_comments()
            if not comments:
                return None

            for comment in comments:
                if comment.get("is_pinned", False):
                    return {
                        "text": comment["text"],
                        "author": comment["author"],
                        "published_at": comment["published_at"],
                        "like_count": comment["like_count"]
                    }

            return None
        except Exception as e:
            raise ValueError(f"Ошибка при получении закрепленного комментария: {e}")

    def get_advertisers(self):
        try:
            advertisers = []
            description_links = self.extract_links(self.metadata.get('description', ''))
            for link in description_links:
                try:
                    matched_brand = self.identify_brand(link)
                    if matched_brand:
                        advertisers.append({
                            "brand": matched_brand,
                            "link": link,
                            "source": "description",
                            "published_at": self.metadata.get('published_at', '')
                        })
                except Exception as e:
                    print(f"Ошибка при обработке ссылки {link}: {e}")

            return advertisers
        except KeyError as e:
            raise ValueError(f"Ошибка в структуре данных метаданных или комментариев: {e}")
        except Exception as e:
            raise ValueError(f"Произошла ошибка при получении рекламодателей: {e}")

    def sanitize_filename(self, name):
        try:
            if not name:
                raise ValueError("Имя файла не может быть пустым.")
            return re.sub(r'[\/:*?"<>|]', '_', name)
        except Exception as e:
            raise ValueError(f"Ошибка при очистке имени файла: {e}")

    def save_advertisers(self):
        try:
            advertisers = self.get_advertisers()
            if not advertisers:
                print("Рекламодатели не найдены.")
                return

            sanitized_title = self.sanitize_filename(self.metadata.get('title', 'unknown_video'))
            advertisers_filename = os.path.join("jsons", f"{sanitized_title}_advertisers.json")

            os.makedirs("jsons", exist_ok=True)

            with open(advertisers_filename, "w", encoding="utf-8") as f:
                json.dump(advertisers, f, ensure_ascii=False, indent=4)

            print(f"Рекламодатели сохранены в {advertisers_filename}")
        except ValueError as e:
            print(f"Ошибка: {e}")
        except Exception as e:
            print(f"Неизвестная ошибка при сохранении рекламодателей: {e}")

    def get_comments(self):
        try:
            comments = []
            request = self.youtube.commentThreads().list(part="snippet,replies", videoId=self.resource_id,
                                                         maxResults=100)
            while request:
                response = request.execute()
                for idx, item in enumerate(response['items']):
                    top_comment = item['snippet']['topLevelComment']['snippet']
                    is_pinned = item['snippet'].get('isPinned', False)
                    if idx == 0 and 'isPinned' not in item['snippet']:
                        is_pinned = True
                    comment_data = {
                        "comment_id": item['snippet']['topLevelComment']['id'],
                        "text": top_comment['textDisplay'],
                        "author": top_comment['authorDisplayName'],
                        "like_count": top_comment['likeCount'],
                        "published_at": top_comment['publishedAt'],
                        "is_pinned": is_pinned,
                        "replies": []
                    }
                    if "replies" in item:
                        for reply in item["replies"]["comments"]:
                            reply_data = {
                                "reply_id": reply['id'],
                                "text": reply['snippet']['textDisplay'],
                                "author": reply['snippet']['authorDisplayName'],
                                "like_count": reply['snippet']['likeCount'],
                                "published_at": reply['snippet']['publishedAt']
                            }
                            comment_data["replies"].append(reply_data)
                    comments.append(comment_data)
                if 'nextPageToken' in response:
                    request = self.youtube.commentThreads().list(
                        part="snippet,replies", videoId=self.resource_id, maxResults=100,
                        pageToken=response['nextPageToken']
                    )
                else:
                    break
            return comments
        except HttpError as e:
            raise ValueError(f"Ошибка при запросе комментариев: {e}")
        except Exception as e:
            raise ValueError(f"Произошла ошибка при получении комментариев: {e}")

    def save_to_json(self):
        try:
            os.makedirs("jsons", exist_ok=True)

            sanitized_title = self.sanitize_filename(self.metadata['title'])
            metadata_filename = os.path.join("jsons", f"{sanitized_title}_metadata.json")
            with open(metadata_filename, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=4)
            print(f"Метаданные видео сохранены в {metadata_filename}")

            comments = self.get_comments()
            comments_filename = os.path.join("jsons", f"{sanitized_title}_comments.json")
            with open(comments_filename, "w", encoding="utf-8") as f:
                json.dump(comments, f, ensure_ascii=False, indent=4)
            print(f"Комментарии видео сохранены в {comments_filename}")
        except Exception as e:
            raise ValueError(f"Ошибка при сохранении данных в JSON: {e}")
