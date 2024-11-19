from youtube_api import YouTubeAPI


def main():
    try:
        api_key = 'YOUR_API_KEY'
        youtube_api = YouTubeAPI(api_key)
        channel_id = input("Введите ID канала: ").strip()
        youtube_channel = youtube_api.get_channel(channel_id)
        print(f"Обрабатываем канал: {youtube_channel.metadata['title']}")
        playlists = youtube_channel.get_playlists()
        if not playlists:
            print("У канала нет плейлистов.")
            return

        print(f"Найдено {len(playlists)} плейлистов.")
        for playlist in playlists:
            print(f"\nОбрабатываем плейлист: {playlist['title']} (ID: {playlist['playlist_id']})")
            try:
                videos = youtube_channel.get_videos_in_playlist(playlist['playlist_id'])
                if not videos:
                    print(f"В плейлисте {playlist['title']} нет видео.")
                    continue

                print(f"Найдено {len(videos)} видео в плейлисте {playlist['title']}.")
                for video in videos:
                    try:
                        video_id = video["video_id"]
                        youtube_video = youtube_api.get_video(video_id)
                        advertisers = youtube_video.get_advertisers()

                        print(f"Видео: {video['title']} (ID: {video_id})")
                        if advertisers:
                            print(f"  Рекламодатели: {advertisers}")
                        else:
                            print("  Рекламодатели не найдены.")

                        youtube_video.save_advertisers()

                    except Exception as e:
                        print(f"Ошибка при обработке видео {video['title']} (ID: {video_id}): {e}")

            except Exception as e:
                print(f"Ошибка при обработке плейлиста {playlist['title']} (ID: {playlist['playlist_id']}): {e}")

    except Exception as e:
        print(f"Ошибка в работе программы: {e}")


if __name__ == "__main__":
    main()
