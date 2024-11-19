from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class YouTubeAPI:
    def __init__(self, api_key):
        try:
            self.youtube = build('youtube', 'v3', developerKey=api_key)
        except HttpError as e:
            raise ValueError(f"Ошибка инициализации YouTube API: {e}")
        except Exception as e:
            raise ValueError(f"Не удалось создать экземпляр YouTube API: {e}")

    def get_video(self, video_id):
        try:
            from youtube_video import YouTubeVideo
            return YouTubeVideo(self.youtube, video_id)
        except Exception as e:
            raise ValueError(f"Ошибка при создании YouTubeVideo: {e}")

    def get_channel(self, channel_id):
        try:
            from youtube_channel import YouTubeChannel
            return YouTubeChannel(self.youtube, channel_id)
        except Exception as e:
            raise ValueError(f"Ошибка при создании YouTubeChannel: {e}")
