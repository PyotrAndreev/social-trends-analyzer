from youtube_resource import YouTubeResource
import json
import os
from googleapiclient.errors import HttpError


class YouTubeChannel(YouTubeResource):
    def __init__(self, youtube, resource_id):
        super().__init__(youtube, resource_id)
        try:
            self.metadata = self._fetch_metadata()
        except HttpError as e:
            raise ValueError(f"Ошибка при запросе метаданных канала: {e}")
        except Exception as e:
            raise ValueError(f"Не удалось инициализировать канал: {e}")

    def _fetch_metadata(self):
        try:
            request = self.youtube.channels().list(
                part="snippet,statistics,contentDetails",
                id=self.resource_id
            )
            response = request.execute()
            if not response['items']:
                raise ValueError("Канал не найден.")
            channel_info = response['items'][0]
            return {
                "title": channel_info['snippet']['title'],
                "description": channel_info['snippet']['description'],
                "subscriber_count": int(channel_info['statistics'].get('subscriberCount', 0)),
                "view_count": int(channel_info['statistics'].get('viewCount', 0)),
            }
        except HttpError as e:
            raise ValueError(f"Ошибка при запросе метаданных канала: {e}")
        except KeyError as e:
            raise ValueError(f"Отсутствуют ожидаемые данные: {e}")
        except Exception as e:
            raise ValueError(f"Произошла ошибка при получении метаданных канала: {e}")

    def get_playlists(self):
        try:
            playlists = []
            request = self.youtube.playlists().list(
                part="snippet",
                channelId=self.resource_id,
                maxResults=50
            )

            while request:
                response = request.execute()
                for item in response['items']:
                    playlists.append({
                        "playlist_id": item['id'],
                        "title": item['snippet']['title'],
                        "description": item['snippet'].get('description', '')
                    })

                if 'nextPageToken' in response:
                    request = self.youtube.playlists().list(
                        part="snippet",
                        channelId=self.resource_id,
                        maxResults=50,
                        pageToken=response['nextPageToken']
                    )
                else:
                    break

            return playlists
        except HttpError as e:
            raise ValueError(f"Ошибка при запросе плейлистов канала: {e}")
        except Exception as e:
            raise ValueError(f"Произошла ошибка при получении плейлистов: {e}")

    def get_videos_in_playlist(self, playlist_id):
        try:
            videos = []
            request = self.youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=50
            )

            while request:
                response = request.execute()
                for item in response['items']:
                    videos.append({
                        "video_id": item['snippet']['resourceId']['videoId'],
                        "title": item['snippet']['title'],
                        "published_at": item['snippet']['publishedAt']
                    })

                if 'nextPageToken' in response:
                    request = self.youtube.playlistItems().list(
                        part="snippet",
                        playlistId=playlist_id,
                        maxResults=50,
                        pageToken=response['nextPageToken']
                    )
                else:
                    break

            return videos
        except HttpError as e:
            raise ValueError(f"Ошибка при запросе видео из плейлиста: {e}")
        except KeyError as e:
            raise ValueError(f"Отсутствуют ожидаемые данные в ответе: {e}")
        except Exception as e:
            raise ValueError(f"Произошла ошибка при получении видео из плейлиста: {e}")

    def save_to_json(self):
        try:
            os.makedirs("jsons", exist_ok=True)

            metadata_filename = os.path.join("jsons", f"{self.metadata['title']}_metadata.json")
            with open(metadata_filename, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=4)
            print(f"Метаданные сохранены в {metadata_filename}")

            playlists = self.get_playlists()
            playlists_filename = os.path.join("jsons", f"{self.metadata['title']}_playlists.json")
            with open(playlists_filename, "w", encoding="utf-8") as f:
                json.dump(playlists, f, ensure_ascii=False, indent=4)
            print(f"Плейлисты сохранены в {playlists_filename}")
        except Exception as e:
            raise ValueError(f"Ошибка при сохранении данных в JSON: {e}")
