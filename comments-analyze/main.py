import os
import googleapiclient.discovery
import openai
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter


def get_youtube_comments(video_id, api_key, max_comments=32768):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    comments = []
    next_page_token = None

    while len(comments) < max_comments:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response.get("items", []):
            comment = item["snippet"]["topLevelComment"]["snippet"]["textOriginal"]
            comments.append(comment)
        
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return comments[:max_comments]

def summarize_comments(comments, api_key):
    openai.api_key = api_key
    summaries = []

    for comment in comments:
        prompt = (
            f"Summarize the following YouTube comment in up to 4 words:\n\n"
            f"Comment: {comment}\n\nSummary:"
        )

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ],
        )
        
        summary = response.choices[0].message["content"].strip()
        summaries.append(summary)
    
    return summaries

def generate_wordcloud(summaries):
    flattened_summaries = [" ".join(words) for words in summaries]
    text = " ".join(flattened_summaries)
    word_counts = Counter(text.split())
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_counts)
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()


if __name__ == "__main__":
    YOUTUBE_API_KEY = "AIzaSyAjsyZtdDt9-yP3x2W5tHiQqEqet1ip3Y4"
    OPENAI_API_KEY = ""
    VIDEO_ID = s"HEwK9XFIzwI"

    print("Получение комментариев с YouTube...")
    comments = get_youtube_comments(VIDEO_ID, YOUTUBE_API_KEY)
    print(f"Получено {len(comments)} комментариев.")

    print("Суммаризация комментариев с помощью ChatGPT...")
    summaries = summarize_comments(comments, OPENAI_API_KEY)
    print(f"Создано {len(summaries)} суммаризаций.")

    print("Создание облака слов...")
    generate_wordcloud(summaries)
    print("Облако слов создано!")