from abc import ABC, abstractmethod


class YouTubeResource(ABC):
    def __init__(self, youtube, resource_id):
        self.youtube = youtube
        self.resource_id = resource_id

    @abstractmethod
    def save_to_json(self):
        pass
